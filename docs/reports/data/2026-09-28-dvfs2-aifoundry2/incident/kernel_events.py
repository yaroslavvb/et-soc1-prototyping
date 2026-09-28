#!/usr/bin/env python3
"""Wall-clock times for the card's error events in the host's kernel log (aifoundry2, read 28 Sep 2026).

    python3 docs/reports/data/2026-09-28-dvfs2-aifoundry2/incident/kernel_events.py [--json]

Inputs, beside this file: kernel-log.txt (its second half: the events with their boot-relative stamps, as `dmesg`
prints them) and clock-anchors.txt (every audit record of the same ring buffer, reduced to its boot-relative stamp and
the epoch time the kernel wrote into it). dmesg -T's own wall times (the first half of kernel-log.txt) add the stamp to
one boot time, and the kernel's boot-relative clock drifts against the wall clock (here by about 0.044 s per hour), so
they are late by up to about 10 s by the 28th. Here each stamp is mapped with the offset (epoch - stamp) interpolated
linearly between the audit records just before and just after it; the +- is half the difference between those two
records' offsets, a bound on the mapping's error, not on when the service processor counted the error: the driver logs
an event when it reads it from the card, which may be later.
"""
import datetime
import json
import os
import re
import sys
import zoneinfo

HERE = os.path.dirname(os.path.abspath(__file__))
TZ = zoneinfo.ZoneInfo("America/Los_Angeles")


def anchors():
    out = []
    for line in open(os.path.join(HERE, "clock-anchors.txt")):
        if line.startswith("#") or not line.strip():
            continue
        up, ep = line.split()
        out.append((float(up), float(ep)))
    return sorted(out)


def events():
    txt = open(os.path.join(HERE, "kernel-log.txt")).read()
    raw = txt.split("\n\n", 1)[1]          # the boot-relative half
    ev, cur = [], None
    for line in raw.splitlines():
        m = re.match(r"\[\s*([\d.]+)\] ET \S+: Error Event Detected", line)
        if m:
            cur = {"stamp_s": float(m.group(1))}
            ev.append(cur)
        elif cur is not None and ":" in line:
            k, v = line.split(":", 1)
            cur[k.strip().lower()] = v.strip()
    return ev


def main():
    A = anchors()
    out = []
    for e in events():
        t = e["stamp_s"]
        before = [a for a in A if a[0] <= t]
        after = [a for a in A if a[0] > t]
        if before and after:
            (u0, e0), (u1, e1) = before[-1], after[0]
            o0, o1 = e0 - u0, e1 - u1
            off = o0 + (o1 - o0) * (t - u0) / (u1 - u0)
            pm = abs(o1 - o0) / 2
        else:
            u0, e0 = (before or after)[-1 if before else 0]
            off, pm = e0 - u0, None
        w = datetime.datetime.fromtimestamp(t + off, TZ)
        out.append({"stamp_s": t, "epoch_s": round(t + off, 3), "pdt": w.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                    "pm_s": None if pm is None else round(pm, 3), "level": e.get("level"), "desc": e.get("desc"),
                    "syndrome": e.get("syndrome")})
    if "--json" in sys.argv:
        json.dump(out, sys.stdout, indent=1)
        print()
        return
    for x in out:
        print(f"{x['pdt']} PDT (+- {x['pm_s']} s)  [{x['stamp_s']:.6f}]  {x['level']}, {x['desc']}: {x['syndrome']}")


if __name__ == "__main__":
    main()
