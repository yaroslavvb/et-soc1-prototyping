#!/usr/bin/env python3
"""V3-DTF camera poller: timestamped, unparsed /frame.csv fetches beside a dtf-cam pass (plan §10).

    nice -n 19 python3 tools/claims-v3/dtf/camera_poll.py --out build/dtf-cam/p1 [--url http://p3-phone:8080/frame.csv]
        [--max-s 900] [--stop-file <path> ...] [--timeout 5]

Runs on aifoundry2 beside the pass, at the lowest priority the scheduler offers. Each iteration fetches
`/frame.csv` (256x192 degC, 393,216 B, 1.03-1.30 s measured) with a hard deadline, stamps it with the host's
`time.time()` at fetch start (t0) and at the last byte (t1) -- the body carries no timestamp of its own -- and
writes the bytes to `<out>/f<t0 in epoch ms>.csv` **unparsed**: nothing in this process ever calls float() on a
frame, because it shares the box with a 10 Hz `ettelem` and a pass that STOPs on a telemetry line older than 3 s
(plan §10: "a poller that blocks on USB or parses in-line could stop a pass for a non-physical reason").
One JSONL line per attempt, successful or not, is appended to `<out>/frames.jsonl`:

    {"t0": <float s>, "t1": <float s>, "bytes": <int>, "ok": <bool>, "n": <int>, "file": "f<ms>.csv",
     "http": <int|null>, "err": <str|null>, "slow": <bool>}

`t0`/`t1` are host epoch seconds, full float precision; the frame's nominal instant is **t0** (the server hands
back the frame it holds when the request arrives, ~0.33 s behind capture per the 17 Oct data guide), which is the
convention `cam_reduce.py --frame-time t0` reads. A failed fetch writes no .csv and one line with `ok: false`.

It never raises on a fetch: every error is logged to `<out>/poll.log` and to stderr, and the loop continues after a
backoff (`--retry-s`, doubling to `--retry-max-s`) so a camera that comes back is picked up again, and a camera
that is gone does not become a hot loop. It stops on: any `--stop-file` appearing, `--max-s` elapsed, SIGTERM or
SIGINT, `--max-frames`, or free space under `--min-free-mb` (frames are 393 KB each, ~1,400 of them in a campaign
~= 550 MB, and filling aifoundry2's disk under a running pass is the one failure worse than losing the camera).
A summary lands in `<out>/done.json` on every exit path.

Frames stay in `build/dtf-cam/` and are never committed (plan §10, §12); `cam_reduce.py` reads them from there.
"""
import argparse
import errno
import json
import os
import signal
import socket
import sys
import time
import urllib.error
import urllib.request

DEFAULT_URL = "http://p3-phone:8080/frame.csv"
FRAME_BYTES = 393216          # measured 20 Oct 2026 and again 21 Oct 00:3x PDT: 192 lines x 256 degC fields
UA = "dtf-camera-poll/1 (et-soc1 V3-DTF)"

_stop = {"why": None}


def _on_signal(sig, frame):
    _stop["why"] = "signal %d" % sig


def fetch(url, timeout, chunk, max_bytes):
    """One fetch with a total deadline. Returns (http_code, body). Raises on anything wrong."""
    t0 = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Connection": "close"})
    parts = []
    got = 0
    r = urllib.request.urlopen(req, timeout=timeout)
    try:
        code = getattr(r, "status", None)
        if code is None:
            code = r.getcode()
        while True:
            if time.time() - t0 > timeout:
                raise socket.timeout("deadline %.2fs exceeded after %d bytes" % (timeout, got))
            b = r.read(chunk)
            if not b:
                break
            parts.append(b)
            got += len(b)
            if max_bytes and got > max_bytes:
                raise ValueError("body over --max-bytes %d" % max_bytes)
    finally:
        try:
            r.close()
        except Exception:
            pass
    return int(code), b"".join(parts)


def free_mb(path):
    try:
        s = os.statvfs(path)
        return (s.f_bavail * s.f_frsize) / 1e6
    except OSError:
        return None


def main():
    p = argparse.ArgumentParser(description="poll the lab thermal camera beside a dtf-cam pass")
    p.add_argument("--out", required=True, help="output directory (per pass, e.g. build/dtf-cam/p1)")
    p.add_argument("--url", default=DEFAULT_URL)
    p.add_argument("--max-s", type=float, default=900.0, help="stop after this many seconds (0 = no limit)")
    p.add_argument("--max-frames", type=int, default=0, help="stop after this many written frames (0 = no limit)")
    p.add_argument("--stop-file", action="append", default=[],
                   help="stop when this file exists; repeatable. Default: <out>/STOP")
    p.add_argument("--timeout", type=float, default=5.0, help="per-fetch deadline, seconds (plan: 5 s)")
    p.add_argument("--interval", type=float, default=0.0,
                   help="minimum seconds between fetch starts (0 = back to back, the measured ~0.45 frame/s)")
    p.add_argument("--retry-s", type=float, default=1.0, help="backoff after a failure, seconds")
    p.add_argument("--retry-max-s", type=float, default=5.0, help="backoff ceiling, seconds")
    p.add_argument("--chunk", type=int, default=262144, help="read chunk, bytes")
    p.add_argument("--max-bytes", type=int, default=8 * FRAME_BYTES, help="refuse a body larger than this")
    p.add_argument("--expect-bytes", type=int, default=FRAME_BYTES,
                   help="a body of another length is still written, flagged short/long in frames.jsonl (0 = off). "
                        "This is a length check, never a parse.")
    p.add_argument("--min-free-mb", type=float, default=2048.0, help="stop if the filesystem drops below this")
    p.add_argument("--log-every", type=int, default=20, help="log one progress line every N frames")
    p.add_argument("--no-nice", action="store_true", help="do not self-renice (the caller already used nice -n 19)")
    p.add_argument("--nice", type=int, default=19, help="target nice value for the self-renice")
    a = p.parse_args()

    os.makedirs(a.out, exist_ok=True)
    stops = list(a.stop_file) or [os.path.join(a.out, "STOP")]
    log = open(os.path.join(a.out, "poll.log"), "a")
    index = open(os.path.join(a.out, "frames.jsonl"), "a")

    def say(msg):
        line = "%s [cam] %s" % (time.strftime("%H:%M:%S"), msg)
        print(line, file=log, flush=True)
        print(line, file=sys.stderr, flush=True)

    # The caller is expected to use `nice -n 19`; do it ourselves too, so a forgotten nice cannot put the poller
    # in front of the pass. Raising the nice value needs no privilege; a failure is not fatal.
    nice_now = None
    if not a.no_nice:
        try:
            cur = os.nice(0)
            if cur < a.nice:
                nice_now = os.nice(a.nice - cur)
            else:
                nice_now = cur
        except OSError as e:
            say("could not renice: %s" % e)
    signal.signal(signal.SIGTERM, _on_signal)
    signal.signal(signal.SIGINT, _on_signal)

    t_start = time.time()
    say("start pid=%d nice=%s url=%s out=%s max_s=%s stop=%s" %
        (os.getpid(), nice_now, a.url, a.out, a.max_s, ",".join(stops)))

    n = ok_n = fail_n = odd_n = 0
    bytes_total = 0
    backoff = a.retry_s
    first_t0 = last_t1 = None
    next_start = 0.0
    while True:
        if _stop["why"]:
            break
        if a.max_s and time.time() - t_start >= a.max_s:
            _stop["why"] = "max-s %.0f" % a.max_s
            break
        hit = [s for s in stops if os.path.exists(s)]
        if hit:
            _stop["why"] = "stop file %s" % hit[0]
            break
        if a.max_frames and ok_n >= a.max_frames:
            _stop["why"] = "max-frames %d" % a.max_frames
            break
        fm = free_mb(a.out)
        if fm is not None and fm < a.min_free_mb:
            _stop["why"] = "free space %.0f MB under --min-free-mb %.0f" % (fm, a.min_free_mb)
            break
        now = time.time()
        if now < next_start:
            time.sleep(min(next_start - now, 0.25))
            continue

        n += 1
        t0 = time.time()
        next_start = t0 + a.interval
        code = err = None
        body = b""
        try:
            code, body = fetch(a.url, a.timeout, a.chunk, a.max_bytes)
            if code != 200:
                raise ValueError("http %s" % code)
            if not body:
                raise ValueError("empty body")
        except Exception as e:                      # never raise on a fetch: log, record, continue
            err = "%s: %s" % (type(e).__name__, e)
            body = b""
        t1 = time.time()

        name = None
        if body and err is None:
            ms = int(t0 * 1000)
            name = "f%d.csv" % ms
            dst = os.path.join(a.out, name)
            k = 0
            while os.path.exists(dst):              # same-millisecond collision; cannot happen at 1 s/frame
                k += 1
                name = "f%d-%d.csv" % (ms, k)
                dst = os.path.join(a.out, name)
            tmp = os.path.join(a.out, "." + name + ".part")
            try:
                fh = open(tmp, "wb")
                try:
                    fh.write(body)                  # unparsed, exactly as the camera sent it
                finally:
                    fh.close()
                os.replace(tmp, dst)                # atomic: a reader never sees a half frame
            except OSError as e:
                err = "write %s: %s" % (errno.errorcode.get(e.errno, e.errno), e)
                name = None
                try:
                    if os.path.exists(tmp):
                        os.unlink(tmp)
                except OSError:
                    pass

        good = err is None and name is not None
        rec = {"t0": t0, "t1": t1, "bytes": len(body), "ok": good, "n": n, "file": name,
               "http": code, "err": err, "slow": bool(t1 - t0 > a.timeout)}
        if a.expect_bytes and good and len(body) != a.expect_bytes:
            rec["len_ok"] = False
            odd_n += 1
        try:
            index.write(json.dumps(rec) + "\n")
            index.flush()
        except OSError as e:
            say("frames.jsonl write failed: %s" % e)

        if good:
            ok_n += 1
            bytes_total += len(body)
            if first_t0 is None:
                first_t0 = t0
            last_t1 = t1
            backoff = a.retry_s
            if a.log_every and ok_n % a.log_every == 0:
                say("%d frames (%.2f/s), last %.2f s, %.0f MB, free %s MB" %
                    (ok_n, ok_n / max(1e-9, t1 - first_t0) if first_t0 and t1 > first_t0 else 0.0,
                     t1 - t0, bytes_total / 1e6, "%.0f" % fm if fm is not None else "?"))
        else:
            fail_n += 1
            say("fetch %d failed after %.2f s: %s (backoff %.1f s)" % (n, t1 - t0, err, backoff))
            end = time.time() + backoff
            while time.time() < end and not _stop["why"]:
                time.sleep(min(0.25, max(0.0, end - time.time())))
            backoff = min(a.retry_max_s, backoff * 2)

    summary = {"out": os.path.abspath(a.out), "url": a.url, "pid": os.getpid(), "nice": nice_now,
               "stopped": _stop["why"], "t_start": t_start, "t_end": time.time(),
               "attempts": n, "frames": ok_n, "failures": fail_n, "odd_length": odd_n,
               "bytes": bytes_total, "first_t0": first_t0, "last_t1": last_t1,
               "rate_per_s": (ok_n / (last_t1 - first_t0)) if (first_t0 and last_t1 and last_t1 > first_t0) else None,
               "args": vars(a)}
    try:
        json.dump(summary, open(os.path.join(a.out, "done.json"), "w"), indent=1)
    except OSError as e:
        say("done.json write failed: %s" % e)
    say("stop (%s): %d frames, %d failures, %.0f MB, %s frame/s" %
        (_stop["why"], ok_n, fail_n, bytes_total / 1e6,
         ("%.2f" % summary["rate_per_s"]) if summary["rate_per_s"] else "?"))
    index.close()
    log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
