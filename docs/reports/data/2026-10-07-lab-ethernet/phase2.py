#!/usr/bin/env python3
"""Second round, run after drive.py: tests that need two or three links busy at once, and a real file copy.

  both ways   aifoundry1 -> 2 and 2 -> 1 at the same time (is the link full duplex?)
  ring        1 -> 2, 2 -> 3 and 3 -> 1 at the same time (does the switch keep every port at full speed?)
  ssh copy    1 GB of data through ssh over Ethernet, and 100 MB over WiFi, timed end to end (what scp/rsync see)
Results are appended to results.jsonl like drive.py's.
"""
import json, subprocess, threading, time
from drive import ADDR, NB, has_ll, record, run_on, target


def all_up(hosts):
    return all(has_ll(h) for h in hosts)


def wait_up(hosts, limit=900):
    end = time.time() + limit
    while time.time() < end:
        if all_up(hosts):
            return True
        time.sleep(3)
    return False


def concurrent(name, pairs, secs=8):
    """Run one 'up' test per (client, server) pair at the same moment; retry the set if any fails."""
    hosts = sorted({h for p in pairs for h in p})
    for attempt in range(1, 9):
        if not wait_up(hosts):
            break
        out = {}

        def one(c, s):
            rc, o, e = run_on(c, f"{NB} up {target(s, 'eth')} --secs {secs}")
            try:
                out[(c, s)] = json.loads(o.strip().splitlines()[-1])
            except Exception:
                out[(c, s)] = None

        ts = [threading.Thread(target=one, args=p) for p in pairs]
        [t.start() for t in ts]
        [t.join() for t in ts]
        if all(out.values()):
            record({"test": name, "path": "eth", "tries": attempt,
                    "links": [{"client": c, "server": s, "Mbps": r["Mbps"], "MBps": r["MBps"]} for (c, s), r in out.items()],
                    "Mbps_total": round(sum(r["Mbps"] for r in out.values()), 1)})
            return
        print(f"retry {name}", flush=True)
        time.sleep(2)
    record({"test": name, "path": "eth", "failed": "no window"})


def ssh_copy(c, s, path, nbytes):
    host = target(s, path)
    dest = f"[{host}]" if ":" in host else host
    cmd = (f"head -c {nbytes} /dev/zero | /usr/bin/time -f %e ssh -o BatchMode=yes -o HostKeyAlias=aifoundry{s} "
           f"yaroslavvb@{host.replace('[', '').replace(']', '')} 'cat > /dev/null'")
    for attempt in range(1, 9):
        if path == "eth" and not wait_up([c, s]):
            break
        rc, o, e = run_on(c, cmd, timeout=600)
        try:
            secs = float(e.strip().splitlines()[-1])
            if rc == 0:
                record({"test": "ssh-copy", "path": path, "client": c, "server": s, "bytes": nbytes, "secs": secs,
                        "MBps": round(nbytes / secs / 1e6, 1), "Mbps": round(nbytes * 8 / secs / 1e6, 1),
                        "tries": attempt})
                return
        except Exception:
            pass
        print(f"retry ssh-copy {path}: rc={rc} {e.strip()[-200:]}", flush=True)
        time.sleep(2)
    record({"test": "ssh-copy", "path": path, "client": c, "server": s, "failed": "no window"})


if __name__ == "__main__":
    # ssh_copy() is not run: over the wired address sshd refuses our keys (between the lab machines `ssh aifoundryN`
    # works only through Tailscale SSH, which rides the tailnet, i.e. WiFi). Kept for when the ports have addresses.
    concurrent("both-ways", [(1, 2), (2, 1)])
    concurrent("ring", [(1, 2), (2, 3), (3, 1)])
