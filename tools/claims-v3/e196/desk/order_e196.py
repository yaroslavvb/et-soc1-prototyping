#!/usr/bin/env python3
"""E196 (Q185, lane reg-e196): the registered run order of every pass, written out (a desk check of code; no device).

    /usr/bin/python3 -I -B order_e196.py ARMS.json HOSTNAME PASSES [--drop F.Ae,Z.b50,I.H.mFFFF] [--commands GEN]

The draw is run_block.py's own, line for line: the pass arms of arms.json in its order, the anchor K.pi and any --drop arm left
out, shuffled by random.Random("<hostname>|<pass>"); a pass runs two burn-in anchors, the anchor, those arms, the anchor. The
draw depends only on the host name string, the pass number and arms.json (Python 3's string seeding hashes the string with
SHA-512, so it is the same under every Python 3 from 3.2; checked here under /usr/bin/python3 3.12.3).
With --commands GEN the registered command of every pass arm on the lab's unchanged sparsity host is printed beside it (E196.md
section 5), and the request's host's command of every train process (make_x14.train_args), GEN standing for the session's gen/.
"""
import argparse
import json
import os
import random
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arms")
    ap.add_argument("host")
    ap.add_argument("passes", type=int)
    ap.add_argument("--drop", default="")
    ap.add_argument("--commands", default=None)
    a = ap.parse_args()
    m = json.load(open(a.arms))
    table = {x["name"]: x for x in m["arms"]}
    drop = [x for x in a.drop.split(",") if x]
    print("# E196 pass order for host %r, passes 0..%d, dropped %s (run_block.py's draw; python %s)" % (
        a.host, a.passes - 1, ",".join(drop) or "-", sys.version.split()[0]))
    for p in range(a.passes):
        arms = [x for x in table if x != "K.pi" and table[x].get("in_passes", True) and x not in drop]
        random.Random("%s|%d" % (a.host, p)).shuffle(arms)
        print("pass %d: K.pi(burn-in) K.pi(burn-in) K.pi(first) %s K.pi(last)" % (p, " ".join(arms)))
    if a.commands:
        g = a.commands
        lab = ["sparsity_host", "--test", "fma", "--type", "fp32", "--pattern", "none"]
        tail = ["--shires", "0xffffffff", "--per-shire", "32", "--seconds", "4", "--stop-file", "OUT/STOP"]
        print("# the lab's unchanged sparsity host, one 4 s run of each pass arm (under timeout 10):")
        for name, t in table.items():
            if not t.get("in_passes", True):
                continue
            if t["tile"] == "builtin:pi":
                vals = "pi"
            elif t["tile"].startswith("lab:"):
                vals = "file:%s/tiles/lab_%s.bin" % (g, t["tile"][4:])
            else:
                vals = "file:%s/tiles/%s" % (g, t["tile"])
            cmd = lab + ["--values", vals] + (["--row-mask", t["row_mask"]] if t["row_mask"] else []) + tail
            print("%-11s %s" % (name, " ".join(cmd)))
        print("# the lab's E78 heater (the approach, every run; under timeout 10):")
        print("heater      " + " ".join(lab + ["--values", "randn", "--shires", "0xffffffff", "--per-shire", "32",
                                               "--seconds", "2", "--seed", "1", "--stop-file", "OUT/STOP"]))
        sys.path.insert(0, os.path.dirname(os.path.abspath(a.arms)))
        here = os.path.dirname(os.path.abspath(__file__))
        src = os.environ.get("X14_SRC")
        if src:
            sys.path.insert(0, src)
            import make_x14
            print("# the request's host (x14_host), the train processes (make_x14.train_args; defaults: all 1,024 minions):")
            for tr in m["trains"]:
                for order in ("SFFS", "FSSF"):
                    print("%s %s   x14_host %s --stop-file OUT/STOP" % (tr["name"], order,
                          " ".join(make_x14.train_args(tr, table, g, order))))
            print("# the request's host, the smoke's premise runs (2 s each, make_x14.host_args):")
            for arm in ("I.H.m00FF", "I.R.m00FF", "Z.a0", "I.R.full"):
                print("%-11s x14_host %s --seconds 2 --stop-file OUT/STOP" % (arm, " ".join(make_x14.host_args(table[arm], g))))


if __name__ == "__main__":
    main()
