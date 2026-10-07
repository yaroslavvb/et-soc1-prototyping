#!/usr/bin/env python3
"""Run the lab's network benchmark from aifoundry1: every pair of machines over Ethernet, WiFi and Tailscale.

The wired ports have no IPv4 address (nothing on that segment runs DHCP), so Ethernet tests use the IPv6
link-local addresses. NetworkManager only keeps those while it retries DHCP (4 tries of 45 s, then 5 min off),
so an Ethernet test waits until both ends have their address and is retried if one vanishes mid-test.
Results: one JSON line per test in results.jsonl.
"""
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
NB = "python3 ~/claude/work/netbench/netbench.py"
# Each machine's addresses, kept out of the public repository: hosts.json beside this file, in the form
# {"1": {"eth": "<IPv6 link-local of enp7s0>", "wifi": "<WiFi LAN address>", "ts": "<tailnet address>"}, "2": ..., "3": ...}
ADDR = {int(k): v for k, v in json.load(open(os.path.join(HERE, "hosts.json"))).items()}
ME = 1
OUT = os.path.join(HERE, "results.jsonl")


def run_on(h, cmd, timeout=90):
    argv = ["bash", "-c", cmd] if h == ME else ["ssh", "-o", "BatchMode=yes", f"aifoundry{h}", cmd]
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


def has_ll(h):
    rc, out, _ = run_on(h, "ip -6 -o addr show dev enp7s0 scope link", 20)
    return ADDR[h]["eth"] in out and "tentative" not in out


def target(h, path):
    return ADDR[h][path] + ("%enp7s0" if path == "eth" else "")


def tests():
    T = []
    for c, s in [(1, 2), (2, 3), (3, 1)]:
        for path in ["eth", "wifi", "ts"]:
            n = 2000 if path == "eth" else 200
            T.append((c, s, path, "rtt", f"rtt {target(s, path)} -n {n}"))
            T.append((c, s, path, "down", f"down {target(s, path)} --secs 8"))
            T.append((c, s, path, "up", f"up {target(s, path)} --secs 8"))
            if path == "eth":
                T.append((c, s, path, "up-P4", f"up {target(s, path)} --secs 8 -P 4"))
    return T


def record(rec):
    rec["t"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    with open(OUT, "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec), flush=True)


def main():
    pending = tests()
    tries = {}
    deadline = time.time() + float(sys.argv[1] if len(sys.argv) > 1 else 3000)
    while pending and time.time() < deadline:
        ll = {h: has_ll(h) for h in ADDR}
        pick = next((t for t in pending if t[2] == "eth" and ll[t[0]] and ll[t[1]]), None)
        if pick is None:
            pick = next((t for t in pending if t[2] != "eth"), None)
        if pick is None:
            time.sleep(3)
            continue
        c, s, path, name, args = pick
        rc, out, err = run_on(c, f"{NB} {args}")
        tries[pick] = tries.get(pick, 0) + 1
        try:
            r = json.loads(out.strip().splitlines()[-1])
            r.update(client=c, server=s, path=path, test=name, tries=tries[pick])
            record(r)
            pending.remove(pick)
        except Exception:
            print(f"retry {c}->{s} {path} {name}: rc={rc} {err.strip()[-200:]}", flush=True)
            if tries[pick] >= 12:
                record({"client": c, "server": s, "path": path, "test": name, "failed": err.strip()[-300:]})
                pending.remove(pick)
            time.sleep(2)
    for t in pending:
        record({"client": t[0], "server": t[1], "path": t[2], "test": t[3], "failed": "not run before deadline"})


if __name__ == "__main__":
    main()
