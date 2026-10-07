#!/usr/bin/env python3
"""Tiny iperf-like TCP benchmark (no install, no root).

  netbench.py serve [--port P] [--seconds S]           sink/source/echo server on [::]:P, exits after S s
  netbench.py up   HOST [--port P] [--secs T] [-P N]   client -> server throughput, N parallel streams
  netbench.py down HOST [--port P] [--secs T] [-P N]   server -> client throughput
  netbench.py rtt  HOST [--port P] [-n N]              TCP request/response round trips, 64-byte messages

HOST may be an IPv6 link-local address with a scope, e.g. fe80::1%enp7s0. Prints one JSON line.
Throughput is counted by the receiver, after a 1 s warm-up is discarded.
"""
import json, socket, socketserver, struct, sys, threading, time

BUF = 1 << 20
CHUNK = memoryview(bytearray(BUF))
WARMUP = 1.0


class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        s = self.request
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        hdr = recv_exact(s, 9)
        mode, secs = hdr[:1], struct.unpack("!d", hdr[1:])[0]
        if mode == b"U":      # client sends; we count and report
            s.sendall(json.dumps(sink(s)).encode())
        elif mode == b"D":    # we send for secs seconds
            source(s, secs)
        elif mode == b"E":    # echo 64-byte messages
            while True:
                m = recv_exact(s, 64)
                if not m:
                    return
                s.sendall(m)


def recv_exact(s, n):
    b = bytearray()
    while len(b) < n:
        x = s.recv(n - len(b))
        if not x:
            return bytes(b) if not b else bytes(b)
        b += x
    return bytes(b)


def sink(s):
    """Read until EOF; return bytes and seconds after the warm-up."""
    buf = bytearray(BUF)
    t0 = time.perf_counter()
    counted, tstart = 0, None
    while True:
        n = s.recv_into(buf)
        if not n:
            break
        now = time.perf_counter()
        if now - t0 >= WARMUP:
            if tstart is None:
                tstart = now
            else:
                counted += n
    tend = time.perf_counter()
    return {"bytes": counted, "secs": (tend - tstart) if tstart else 0.0}


def source(s, secs):
    end = time.perf_counter() + secs
    try:
        while time.perf_counter() < end:
            s.sendall(CHUNK)
    except OSError:
        pass
    try:
        s.shutdown(socket.SHUT_WR)
    except OSError:
        pass


def connect(host, port):
    for fam, typ, proto, _, addr in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM):
        s = socket.socket(fam, typ, proto)
        s.settimeout(10)
        s.connect(addr)
        s.settimeout(None)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        return s
    raise OSError("no address")


def throughput(host, port, mode, secs, streams):
    results = [None] * streams

    def one(i):
        s = connect(host, port)
        s.sendall(mode + struct.pack("!d", secs + WARMUP))
        if mode == b"U":
            source(s, secs + WARMUP)
            results[i] = json.loads(s.recv(4096).decode())
        else:
            results[i] = sink(s)
        s.close()

    ts = [threading.Thread(target=one, args=(i,)) for i in range(streams)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    if any(r is None for r in results):
        raise OSError("a stream failed")
    total = sum(r["bytes"] / r["secs"] for r in results if r["secs"] > 0)
    return {"mode": "up" if mode == b"U" else "down", "streams": streams, "secs": secs,
            "MBps": round(total / 1e6, 1), "Mbps": round(total * 8 / 1e6, 1)}


def rtt(host, port, n):
    s = connect(host, port)
    s.sendall(b"E" + struct.pack("!d", 0))
    msg = b"x" * 64
    for _ in range(20):          # warm-up
        s.sendall(msg); recv_exact(s, 64)
    ts = []
    for _ in range(n):
        t = time.perf_counter()
        s.sendall(msg); recv_exact(s, 64)
        ts.append((time.perf_counter() - t) * 1e6)
    s.close()
    ts.sort()
    return {"mode": "rtt", "n": n, "us_min": round(ts[0], 1), "us_p50": round(ts[n // 2], 1),
            "us_p99": round(ts[int(n * 0.99)], 1), "us_max": round(ts[-1], 1)}


class Server(socketserver.ThreadingTCPServer):
    address_family = socket.AF_INET6
    allow_reuse_address = True
    daemon_threads = True

    def server_bind(self):
        self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        super().server_bind()


def main(a):
    def opt(name, default, cast=int):
        return cast(a[a.index(name) + 1]) if name in a else default
    port = opt("--port", 47801)
    if a[0] == "serve":
        srv = Server(("::", port), Handler)
        threading.Timer(opt("--seconds", 3600), srv.shutdown).start()
        srv.serve_forever()
        return
    host = a[1]
    if a[0] in ("up", "down"):
        r = throughput(host, port, b"U" if a[0] == "up" else b"D", opt("--secs", 8, float), opt("-P", 1))
    else:
        r = rtt(host, port, opt("-n", 2000))
    r["host"] = host
    print(json.dumps(r), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
