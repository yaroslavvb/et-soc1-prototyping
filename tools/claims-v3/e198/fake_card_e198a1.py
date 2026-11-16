#!/usr/bin/env python3
"""E198's stand-ins after dated amendment A1 (Q196, lane a1-e198, Mon 16 Nov 2026, before any E198 datum), for the desk tests ONLY
(desk/desktest_realpath_e198a1.py, rb/selftest_rb_e198a1.sh): fake_card_e198.py (kit-e198, unchanged beside it, imported by its path) with
two knobs more, for A1's kill path. Every role and knob of fake_card_e198.py is its own, unchanged; small wrappers named as the box's tools
exec `python3 -I -B fake_card_e198a1.py <role> "$@"`, so a wrapper keeps its process ID.

  STATE/a1-hang  "<call> <life seconds> [<grace seconds>]": THE HOST THAT HANGS PAST ITS TERM. The host's <call>-th call (counted in
                 STATE/host-calls with every other call) opens /dev/et<ET_DEVICES>_ops and prints the runtime's line as the real host does,
                 then launches nothing: it catches SIGTERM (it records each one, with its second, in STATE/a1-host-signals.log, and does
                 not end on it) and ENDS BY ITSELF, exit 0, <life> seconds after it started, or <grace> seconds after its first TERM when
                 a grace is given (the host that ends 1.5 s after its TERM, which v1's one-second KILL after the TERM would have ended at
                 11 s). Its start, every TERM and its own end go to STATE/a1-host.log; a process ended by a KILL cannot write that end
                 line, so the line is the proof it was not killed. Its process ID goes to STATE/a1-host.pid.
  STATE/a1-sampler-end  (a file) while a stand-in sampler runs: it ends by itself, as at its --seconds (a thread sees the file and sends
                 its own process a SIGTERM, which fake_card_e198.py's sampler takes as its stop), and notes it in STATE/a1-sampler.log. The
                 desk test makes it only after the session has ended. Since the dated fix K9 (Q196, fix-a1e198) the runner's clean-up
                 stops its sampler even when a device process did not end, so the knob finds no sampler and the note stays empty (the
                 HG case asserts it); the knob stays as a safety net, so a case never leaves a sampler behind.
EVERY WATT AND DEGREE IS fake_card_e198.py's ARBITRARY TEST VALUE, NOT A FORECAST AND NOT A MEASUREMENT. Nothing here opens a device: the
desk tests bind /dev/null at the card nodes' paths inside a sandbox with no card. Nothing here sends a KILL to anything.
SPDX-License-Identifier: Apache-2.0
"""
import importlib.util
import os
import signal
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("fake_card_e198_for_a1", os.path.join(HERE, "fake_card_e198.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)
STATE = F.STATE


def st(name):
    return os.path.join(STATE, name)


def note(name, msg):
    if STATE:
        with open(st(name), "a") as f:
            f.write(f"{time.time():.3f} {msg}\n")


def hang_spec():
    """(call, life, grace or None) from STATE/a1-hang, or None."""
    t = F.read("a1-hang").split()
    if len(t) < 2:
        return None
    try:
        return int(t[0]), float(t[1]), (float(t[2]) if len(t) > 2 else None)
    except ValueError:
        return None


def host(argv):
    spec = hang_spec()
    n_call = int(F.read("host-calls").strip() or 0) + 1
    if spec is None or spec[0] != n_call:
        return F.host(argv)                    # fake_card_e198.py's host, unchanged (it counts the call itself)
    _call, life, grace = spec
    with open(st("host-calls"), "w") as f:
        f.write(str(n_call))
    F.log("host " + " ".join(argv) + " (A1 hang: call %d, life %g s, grace %s)" % (n_call, life, "none" if grace is None else "%g s" % grace))
    sel = os.environ.get("ET_DEVICES") or "0"
    t0 = time.time()
    with open(st("a1-host.pid"), "w") as f:
        f.write(str(os.getpid()))
    note("a1-host.log", f"A1-HOST start pid {os.getpid()} call {n_call} (life {life:g} s, grace {grace})")
    terms = []

    def on_term(_signum, _frame):
        terms.append(time.time() - t0)
        note("a1-host-signals.log", "TERM %.3f s after the start" % terms[-1])
        note("a1-host.log", "A1-HOST TERM at %.3f s: caught, not ended on it" % terms[-1])
    signal.signal(signal.SIGTERM, on_term)
    fd = os.open("/dev/et%s_ops" % sel, os.O_RDONLY)          # held as the real host holds the ops node
    out = sys.stdout.buffer
    out.write(F.runtime_bytes())                               # aifoundry1's form: the runtime's line when the device opens
    out.flush()
    print(f"PCIe target:                                               /dev/et{sel}_ops\n"
          f"Physical device ID:                                        {sel}                    (0x{sel})", file=sys.stderr)
    print("device ready (stand-in A1 hang: no launch follows)", file=sys.stderr)
    while True:
        now = time.time() - t0
        if now >= life:
            why = f"its life of {life:g} s"
            break
        if grace is not None and terms and now >= terms[0] + grace:
            why = f"{grace:g} s after its first TERM"
            break
        time.sleep(0.05)
    os.close(fd)
    note("a1-host.log", "A1-HOST ended by itself at %.3f s (%s): %d TERM(s) received, exit 0" % (time.time() - t0, why, len(terms)))
    return 0


def ettelem(argv):
    if argv[:1] == ["sample"]:
        me = os.getpid()

        def watch():
            while not os.path.exists(st("a1-sampler-end")):
                time.sleep(0.2)
            note("a1-sampler.log", f"A1-SAMPLER pid {me}: the end knob seen: ending by itself (its own SIGTERM, its stop)")
            os.kill(me, signal.SIGTERM)                        # to itself: fake_card_e198.py's sampler ends on it, as at its --seconds
        threading.Thread(target=watch, daemon=True).start()
    return F.ettelem(argv)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    role, argv = sys.argv[1], sys.argv[2:]
    if role == "host":
        return host(argv)
    if role == "ettelem":
        return ettelem(argv)
    if role == "etwho":
        return F.etwho(argv)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
