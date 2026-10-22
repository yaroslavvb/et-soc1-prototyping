#!/usr/bin/env python3
"""record_cam.py - E62 heat movies: record the thermal camera's lossless stream beside a card run.

    nice -n 19 python3 record_cam.py --url http://p3-phone:8080/stream.raw.z --out <RUNDIR>/cam \
        --stop-file <path> --max-s <s> [--status-every 5] [--min-free-mb 5000]

Runs on the box the camera is wired to, at the lowest priority the scheduler offers, for the whole
session - one recording, not one per block, so every frame carries the same clock and nothing is
lost between blocks.

What it writes, all of it appended so a restart into the same directory continues the recording
----------------------------------------------------------------------------------------------
    cam/cam.p3rec     repeat { uint64 LE host_recv_ns ; uint32 LE len ; len bytes of the zlib blob
                      exactly as the phone sent it }. `host_recv_ns` is `time.time_ns()` here when
                      the blob's last byte arrived: the session's clock, the same one the runner
                      stamps its launches with, so alignment needs no cross-machine offset.
                      Restarting into the same directory continues this file: the recorder walks
                      the existing record headers (12 bytes each, never a blob), logs the gap since
                      the last frame already on disk, and drops a half-written tail record left by
                      a killed process - which would otherwise hide every frame appended after it.
    cam/status.jsonl  one line per GET /health: fps, pictureHealthy, frozenFrameCount, preset, ...
    cam/gaps.jsonl    one line per event, each with its host `t`: `connect`, `connect_failed`,
                      `disconnect` (with why, the frames that connection carried, and the bytes of
                      any half-read frame discarded), `gap` (the first frame back after a break,
                      with the gap in seconds and a frame count estimated at 25 fps) and `stop`.
                      Because this process never parses a frame it cannot name the sequence numbers
                      it missed; `p3rec.py summarize` gives the exact count from the headers.
    cam/done.json     the last recorder process's summary: packets, bytes, seconds, first/last host
                      time, reconnects, why it stopped (every process also appends its summary to
                      gaps.jsonl as a `stop` event, so a restart keeps the history). `mono_s` and
                      `clock_steps` witness that the host wall clock - the clock every timestamp
                      here and every launch time use - did not step mid-session.
    cam/record.log    the human log, also on stderr
    cam/recorder.lock the running recorder's pid, held under an exclusive flock for its lifetime

Rules it keeps
--------------
* **It never parses a frame.** The only thing it reads out of the stream is the 4-byte little-endian
  length prefix; the blob goes to disk compressed and untouched. No zlib, no numpy, no array in this
  process. Decoding happens later, in `p3rec.py`, off the critical path - this process shares the box
  with a 10 Hz telemetry sampler and a card run that stops if a telemetry line goes stale.
* **It only ever reads, and only two paths.** `--url` must name one of `STREAM_PATHS` exactly, and
  `/health` is derived from its host and port, so the only requests this process can make are
  `GET /stream.raw.z` (or `/stream.diff.z`) and `GET /health`. Anything else - `/api/control`, and
  equally `/API/control`, `//api/control`, `/a%70i/control`, `/x/../api/control`, a non-http scheme
  - is refused before the output directory is created. Redirects are refused too, so the phone
  cannot be talked into sending us somewhere else. The camera's preset, emissivity and auto-FFC are
  therefore exactly as the public live page has them.
* **One recorder per directory.** It takes an exclusive `flock` on `<out>/recorder.lock` and refuses
  to start if another recorder holds it. Two recorders appending to one `cam.p3rec` would interleave
  duplicate frames (which read downstream as frozen planes, i.e. as false shutter events) and the
  second one's tail repair would truncate the first one's data mid-write.
* **It reconnects.** A dropped, stalled or desynced stream is logged with its times and retried with
  a doubling backoff, forever, until a stop condition. A frame that was half-read when the
  connection died is discarded, never half-written.
* **It stops** on any `--stop-file` appearing, on `--max-s`, on SIGTERM/SIGINT, or when free space
  falls under `--min-free-mb` - and writes `done.json` on every one of those paths. At 25 fps the
  stream costs ~1.0 MB/s, i.e. ~3.6 GB an hour, so the disk check is not decoration.

Stop-file latency is at most `--stop-every` (0.25 s by default) while frames are arriving, and at
most `--timeout` while the stream is stalled: a signal handler only sets a flag, and a blocked
`read` resumes rather than aborting, so the read deadline is what bounds a stalled stop.
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import struct
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

try:
    import fcntl
except ImportError:                   # not posix: the one-recorder lock is then unavailable
    fcntl = None

DEFAULT_URL = "http://p3-phone:8080/stream.raw.z"
# The only paths this tool will ever GET, besides the /health it derives from the stream's host.
# Both are framed as `uint32 LE length ; blob`, which is the framing written to the .p3rec.
STREAM_PATHS = ("/stream.raw.z", "/stream.diff.z")
HEALTH_PATH = "/health"
REC = struct.Struct("<QI")            # host_recv_ns, len
LEN = struct.Struct("<I")             # the stream's length prefix
MAX_BLOB = 1_000_000                  # a compressed frame is ~40 KB; this is the desync detector
UA = "hm-record-cam/1 (et-soc1 E62)"

_stop = {"why": None}


def _on_signal(sig, _frame):
    _stop["why"] = "signal %d" % sig


class _NoRedirects(urllib.request.HTTPRedirectHandler):
    """Refuse every redirect: a 3xx is the one way a GET of an allowed path could end up fetching
    something else (an `/api/*` control endpoint, or another host)."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code,
                                     "refusing a %s redirect to %s" % (code, newurl), headers, fp)


OPENER = urllib.request.build_opener(_NoRedirects)


def get(url: str, timeout: float):
    """The only HTTP call in this file. No redirects, and the URL that answers must be the one asked
    for."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Connection": "close"})
    resp = OPENER.open(req, timeout=timeout)
    got = resp.geturl()
    if got != url:
        try:
            resp.close()
        finally:
            raise ValueError("served %s instead of %s" % (got, url))
    return resp


def check_url(url: str):
    """None if `url` is one of the two endpoints this tool may read, else why it is refused."""
    u = urllib.parse.urlsplit(url)
    if u.scheme != "http":
        return "scheme %r is not http" % u.scheme
    if not u.netloc:
        return "no host in the URL"
    # Unquote before judging, so /a%70i/control cannot slip past a prefix test, and compare the
    # whole path against the allowlist rather than testing for a forbidden prefix.
    path = urllib.parse.unquote(u.path)
    if path not in STREAM_PATHS:
        extra = ""
        if "api" in path.lower():
            extra = " - the camera's control surface (/api/*) is out of bounds for this tool"
        return "path %r is not one of %s%s" % (path, ", ".join(STREAM_PATHS), extra)
    return None


def free_mb(path: str):
    try:
        s = os.statvfs(path)
        return (s.f_bavail * s.f_frsize) / 1e6
    except OSError:
        return None


def _write_all(fd: int, data: bytes) -> int:
    """Write every byte of `data` to `fd` (O_APPEND), looping over partial writes."""
    mv = memoryview(data)
    n = 0
    while n < len(mv):
        n += os.write(fd, mv[n:])
    return n


class ShortRead(Exception):
    """The server closed the connection in the middle of a frame."""

    def __init__(self, got: int, want: int):
        super().__init__("stream closed after %d of %d bytes" % (got, want))
        self.partial_bytes = got


def _read_exact(fp, n: int, base: int = 0) -> bytes:
    """Read exactly n bytes or raise, tagging the exception with how much of the frame was read.

    `base` is what had already been consumed for this frame, so `partial_bytes` on the raised
    exception is always the whole discarded prefix.
    """
    parts = []
    got = 0
    while got < n:
        try:
            b = fp.read(n - got)
        except Exception as e:                      # timeout, reset, anything: keep the count
            e.partial_bytes = base + got
            raise
        if not b:
            raise ShortRead(base + got, n)
        parts.append(b)
        got += len(b)
    return b"".join(parts) if len(parts) > 1 else parts[0]


def scan_tail(path: str):
    """Walk an existing recording's record headers -> (records, last_recv_ns, good_end_offset).

    Only the 12-byte `.p3rec` record headers are read - the framing this process writes itself -
    and each blob is skipped with a seek. No blob is ever read back and nothing is decoded.

    `good_end_offset` is the end of the last whole record. A process killed mid-write leaves a
    partial record; appending after it would make every later frame unreachable to a reader that
    stops at the first bad record, so the caller truncates to this offset first.
    """
    recs, last_ns, good = 0, None, 0
    with open(path, "rb") as f:
        size = os.fstat(f.fileno()).st_size
        while True:
            hb = f.read(REC.size)
            if len(hb) < REC.size:
                break
            recv_ns, n = REC.unpack(hb)
            if not 0 < n < MAX_BLOB:
                break                              # desynced: stop at the last good boundary
            end = f.tell() + n
            if end > size:
                break                              # the tail record is incomplete
            f.seek(n, os.SEEK_CUR)
            recs += 1
            last_ns = recv_ns
            good = end
    return recs, last_ns, good


def health_url_for(stream_url: str) -> str:
    """`/health` on the same host and port as the stream. The only other endpoint we ever touch."""
    u = urllib.parse.urlsplit(stream_url)
    return urllib.parse.urlunsplit((u.scheme, u.netloc, HEALTH_PATH, "", ""))


def take_lock(path: str):
    """An exclusive, non-blocking flock on `path` -> (fd, None) or (None, why).

    The lock is released by the kernel when this process exits however it exits, so a lock left by a
    crashed recorder is never stale. The holder's pid and start time are written into the file for
    the refusal message.
    """
    if fcntl is None:
        return None, "fcntl is unavailable on this platform"
    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        try:
            held = os.read(fd, 400).decode("utf-8", "replace").strip()
        except OSError:
            held = ""
        os.close(fd)
        return None, "another recorder holds %s%s" % (path, (" (%s)" % held) if held else "")
    os.ftruncate(fd, 0)
    os.write(fd, json.dumps({"pid": os.getpid(), "t_start": time.time()}).encode() + b"\n")
    return fd, None


HEALTH_KEYS = ("ok", "connected", "streaming", "pictureHealthy", "frozenFrameCount", "fps",
               "lastFrameAgeMs", "framesRead", "preset", "mode", "nuctBypass", "verifiedGood",
               "resourceStatus", "cpuUsedPct", "memAvailableMb", "appVersion")


class StatusPoller(threading.Thread):
    """GET /health every `every` seconds into status.jsonl. A daemon thread, so it can never hold
    the recording up: a slow or missing phone shows as a line with an `err` and nothing else."""

    def __init__(self, url: str, path: str, every: float, timeout: float, say):
        super().__init__(name="health", daemon=True)
        self.url, self.path, self.every, self.timeout, self.say = url, path, every, timeout, say
        self.n = self.fail = 0
        self.last = None

    def run(self):
        while not _stop["why"]:
            t0 = time.time()
            rec = {"t": t0, "url": self.url}
            try:
                with get(self.url, self.timeout) as r:
                    body = r.read(1 << 16)
                    rec["http"] = getattr(r, "status", None) or r.getcode()
                h = json.loads(body.decode("utf-8", "replace"))
                rec.update({k: h[k] for k in HEALTH_KEYS if k in h})
                rec["fetch_ms"] = round((time.time() - t0) * 1000, 1)
                self.n += 1
                self.last = rec
            except Exception as e:                      # a health failure never touches the stream
                rec["err"] = "%s: %s" % (type(e).__name__, e)
                rec["fetch_ms"] = round((time.time() - t0) * 1000, 1)
                self.fail += 1
                if self.fail <= 3 or self.fail % 20 == 0:
                    self.say("health fetch failed (%d): %s" % (self.fail, rec["err"]))
            try:
                with open(self.path, "a") as f:
                    f.write(json.dumps(rec) + "\n")
            except OSError as e:
                self.say("status.jsonl write failed: %s" % e)
            end = t0 + self.every
            while time.time() < end and not _stop["why"]:
                time.sleep(min(0.25, max(0.0, end - time.time())))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="record the lab thermal camera's lossless stream")
    p.add_argument("--url", default=DEFAULT_URL, help="the stream endpoint (default: %s)" % DEFAULT_URL)
    p.add_argument("--out", required=True, help="output directory, e.g. <RUNDIR>/cam")
    p.add_argument("--max-s", type=float, default=0.0, help="stop after this many seconds (0 = no limit)")
    p.add_argument("--stop-file", action="append", default=[],
                   help="stop when this file exists; repeatable. Always also <out>/STOP")
    p.add_argument("--max-packets", type=int, default=0, help="stop after this many frames (0 = no limit)")
    p.add_argument("--timeout", type=float, default=5.0,
                   help="socket timeout, seconds: a stream quiet for this long is treated as dropped")
    p.add_argument("--connect-timeout", type=float, default=10.0, help="connect deadline, seconds")
    p.add_argument("--status-every", type=float, default=5.0,
                   help="GET /health this often, seconds (0 = never)")
    p.add_argument("--status-timeout", type=float, default=4.0)
    p.add_argument("--min-free-mb", type=float, default=5000.0,
                   help="stop if the filesystem drops below this (the stream costs ~1.0 MB/s)")
    p.add_argument("--retry-s", type=float, default=0.5,
                   help="first reconnect backoff, seconds. Keep it above one frame time (0.04 s): "
                        "the phone serves the newest frame and resets its own last-sent sequence "
                        "per connection, so a reconnect inside one frame time re-serves the frame "
                        "already recorded (p3rec reports that as `seq repeated`)")
    p.add_argument("--retry-max-s", type=float, default=5.0, help="reconnect backoff ceiling, seconds")
    p.add_argument("--disk-every", type=float, default=2.0, help="check free space this often, seconds")
    p.add_argument("--stop-every", type=float, default=0.25,
                   help="look for the stop files this often, seconds (this bounds the stop latency)")
    p.add_argument("--log-every", type=int, default=250, help="one progress line every N frames (0 = off)")
    p.add_argument("--name", default="cam.p3rec", help="the recording's file name inside --out")
    p.add_argument("--no-nice", action="store_true", help="do not self-renice (the caller used nice -n 19)")
    p.add_argument("--nice", type=int, default=19)
    a = p.parse_args(argv)

    why = check_url(a.url)
    if why is not None:
        print("refusing --url %s: %s.\nThis tool reads only %s and %s on the same host."
              % (a.url, why, " or ".join(STREAM_PATHS), HEALTH_PATH), file=sys.stderr)
        return 2

    os.makedirs(a.out, exist_ok=True)
    rec_path = os.path.join(a.out, a.name)
    stops = list(dict.fromkeys(list(a.stop_file) + [os.path.join(a.out, "STOP")]))
    lock_fd, held = take_lock(os.path.join(a.out, "recorder.lock"))
    if lock_fd is None and fcntl is not None:
        print("refusing to record into %s: %s" % (os.path.abspath(a.out), held), file=sys.stderr)
        return 3
    log = open(os.path.join(a.out, "record.log"), "a")
    gaps = open(os.path.join(a.out, "gaps.jsonl"), "a")

    def say(msg):
        line = "%s [rec] %s" % (time.strftime("%H:%M:%S"), msg)
        print(line, file=log, flush=True)
        print(line, file=sys.stderr, flush=True)

    def event(kind, **kw):
        line = dict(kind=kind, t=time.time(), **kw)
        try:
            gaps.write(json.dumps(line) + "\n")
            gaps.flush()
        except OSError as e:
            say("gaps.jsonl write failed: %s" % e)
        return line

    if lock_fd is None:
        say("WARNING: %s; nothing stops a second recorder writing into this directory" % held)
    nice_now = None
    if not a.no_nice:
        try:
            cur = os.nice(0)
            nice_now = os.nice(a.nice - cur) if cur < a.nice else cur
        except OSError as e:
            say("could not renice: %s" % e)
    signal.signal(signal.SIGTERM, _on_signal)
    signal.signal(signal.SIGINT, _on_signal)

    before = os.path.getsize(rec_path) if os.path.exists(rec_path) else 0
    packets_before, prev_last_ns, repaired = 0, None, 0
    if before:
        packets_before, prev_last_ns, good_end = scan_tail(rec_path)
        if good_end < before:
            repaired = before - good_end
            os.truncate(rec_path, good_end)        # drop the half-written record, keep the rest
            before = good_end
    t_start = time.time()
    say("start pid=%d nice=%s url=%s out=%s max_s=%s stop=%s append_at=%d B (%d packets already)"
        % (os.getpid(), nice_now, a.url, os.path.abspath(a.out), a.max_s or "none",
           ",".join(stops), before, packets_before))
    if before:
        event("append", p3rec=os.path.abspath(rec_path), p3rec_bytes_before=before,
              packets_before=packets_before,
              last_recv_s=(prev_last_ns / 1e9) if prev_last_ns else None,
              repaired_bytes=repaired)
        if repaired:
            say("repaired %s: dropped a %d-byte partial record left by an earlier process"
                % (a.name, repaired))

    poller = None
    if a.status_every > 0:
        poller = StatusPoller(health_url_for(a.url), os.path.join(a.out, "status.jsonl"),
                              a.status_every, a.status_timeout, say)
        poller.start()

    fd = os.open(rec_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    packets = blob_bytes = 0
    conns = conn_fails = partial_n = gaps_n = clock_steps = 0
    gap_s_total = 0.0
    first_recv_ns = last_recv_ns = None
    mono_first = mono_last = None
    backoff = a.retry_s
    next_disk = next_stop = 0.0
    free_now = None

    def stop_check() -> bool:
        # The stop files are polled on their own, much shorter, period: the disk check costs a
        # statvfs and does not need to run four times a second, but the stop latency is what the
        # runner waits on when it is shutting a session down.
        nonlocal next_disk, next_stop, free_now
        if _stop["why"]:
            return True
        if a.max_s and time.time() - t_start >= a.max_s:
            _stop["why"] = "max-s %g" % a.max_s
            return True
        if a.max_packets and packets >= a.max_packets:
            _stop["why"] = "max-packets %d" % a.max_packets
            return True
        now = time.time()
        if now >= next_stop:
            next_stop = now + a.stop_every
            for s in stops:
                if os.path.exists(s):
                    _stop["why"] = "stop file %s" % s
                    return True
        if now >= next_disk:
            next_disk = now + a.disk_every
            free_now = free_mb(a.out)
            if free_now is not None and free_now < a.min_free_mb:
                _stop["why"] = "free space %.0f MB under --min-free-mb %.0f" % (free_now, a.min_free_mb)
                return True
        return False

    try:
        while not stop_check():
            conns += 1
            conn_id = conns
            t_open = time.time()
            # Across a restart into the same directory the break is measured against the last frame
            # the previous process wrote, so the gap is logged there too.
            recv_before_gap = last_recv_ns if last_recv_ns is not None else prev_last_ns
            resp = None
            try:
                resp = get(a.url, a.connect_timeout)
                code = getattr(resp, "status", None) or resp.getcode()
                if code != 200:
                    raise ValueError("http %s" % code)
                try:                 # retighten the socket to the per-read deadline, if we can
                    resp.fp.raw._sock.settimeout(a.timeout)
                except Exception:    # not fatal: the connect timeout then governs the reads too
                    if conn_id == 1:
                        say("could not retighten the socket timeout; reads use %.1f s"
                            % a.connect_timeout)
            except Exception as e:
                conn_fails += 1
                err = "%s: %s" % (type(e).__name__, e)
                event("connect_failed", conn=conn_id, err=err, backoff_s=backoff,
                      connect_failures=conn_fails)
                say("connect %d failed: %s (backoff %.1f s)" % (conn_id, err, backoff))
                if resp is not None:
                    try:
                        resp.close()
                    except Exception:
                        pass
                end = time.time() + backoff
                while time.time() < end and not stop_check():
                    time.sleep(min(0.25, max(0.0, end - time.time())))
                backoff = min(a.retry_max_s, backoff * 2)
                continue

            event("connect", conn=conn_id, url=a.url, packets_so_far=packets,
                  connect_s=round(time.time() - t_open, 3))
            say("connected (%d) after %.2f s" % (conn_id, time.time() - t_open))
            backoff = a.retry_s
            in_conn = 0
            partial = 0
            disc = None
            try:
                while True:
                    if stop_check():
                        disc = "stop: %s" % _stop["why"]
                        break
                    lb = _read_exact(resp, LEN.size)
                    (clen,) = LEN.unpack(lb)
                    if not 0 < clen < MAX_BLOB:
                        raise ValueError("desync: frame length %d" % clen)
                    blob = _read_exact(resp, clen, base=LEN.size)
                    recv_ns = time.time_ns()       # the last byte of the frame is in hand
                    mono = time.monotonic()
                    try:
                        _write_all(fd, REC.pack(recv_ns, clen) + blob)   # one write, O_APPEND
                    except OSError as e:
                        # A full or broken disk is not something to reconnect through: stop, so the
                        # session's stop reason says what happened instead of a reconnect loop.
                        # A write that failed part way through leaves a torn record, which hides
                        # every frame behind it from a reader that stops at the first bad record,
                        # so cut the file back to the last whole one.
                        _stop["why"] = "write failed: %s" % e
                        good = before + packets * REC.size + blob_bytes
                        try:
                            if os.path.getsize(rec_path) > good:
                                os.truncate(rec_path, good)
                                say("write failed mid-record: cut %s back to %d B (%d packets)"
                                    % (a.name, good, packets_before + packets))
                        except OSError as e2:
                            say("could not cut the torn tail back: %s" % e2)
                        raise
                    packets += 1
                    in_conn += 1
                    blob_bytes += clen
                    if first_recv_ns is None:
                        first_recv_ns, mono_first = recv_ns, mono
                    elif abs((recv_ns - last_recv_ns) / 1e9 - (mono - mono_last)) > 0.25:
                        # time.time_ns() is the clock every launch time is stamped with, so a step
                        # in it (ntp, a manual set) moves the whole alignment. The monotonic clock
                        # is the witness.
                        clock_steps += 1
                        if clock_steps <= 5:
                            event("clock_step", conn=conn_id, packets=packets,
                                  wall_dt_s=round((recv_ns - last_recv_ns) / 1e9, 6),
                                  mono_dt_s=round(mono - mono_last, 6))
                            say("the host wall clock stepped: %.3f s of wall time in %.3f s of "
                                "monotonic time" % ((recv_ns - last_recv_ns) / 1e9, mono - mono_last))
                    last_recv_ns, mono_last = recv_ns, mono
                    if in_conn == 1 and recv_before_gap is not None:
                        # The first frame back after a break. The recorder never parses a frame, so
                        # it cannot say which sequence numbers were missed - it logs the times and
                        # an estimate at the nominal 25 fps; `p3rec.py summarize` gives the exact
                        # count from the headers' seq afterwards.
                        gap_s = (recv_ns - recv_before_gap) / 1e9
                        gaps_n += 1
                        gap_s_total += gap_s
                        event("gap", conn=conn_id, gap_s=round(gap_s, 4),
                              last_before_s=recv_before_gap / 1e9, first_after_s=recv_ns / 1e9,
                              missed_frames_est=max(0, int(round(gap_s * 25.0)) - 1),
                              gaps_so_far=gaps_n)
                        say("stream resumed after %.3f s (~%d frames missed)"
                            % (gap_s, max(0, int(round(gap_s * 25.0)) - 1)))
                    if a.log_every and packets % a.log_every == 0:
                        span = (last_recv_ns - first_recv_ns) / 1e9
                        say("%d packets, %.2f fps, %.0f MB, conn %d, free %s MB"
                            % (packets, (packets - 1) / span if span > 0 else 0.0,
                               blob_bytes / 1e6, conn_id,
                               "%.0f" % free_now if free_now is not None else "?"))
            except Exception as e:
                disc = "%s: %s" % (type(e).__name__, e)
                partial = int(getattr(e, "partial_bytes", 0) or 0)
            finally:
                try:
                    resp.close()
                except Exception:
                    pass
            if partial:
                partial_n += 1
            event("disconnect", conn=conn_id, why=disc, packets_in_conn=in_conn,
                  conn_s=round(time.time() - t_open, 3), packets=packets,
                  last_recv_s=(last_recv_ns / 1e9) if last_recv_ns else None,
                  discarded_partial_bytes=partial)
            say("connection %d ended after %d packets: %s" % (conn_id, in_conn, disc))
            if _stop["why"]:
                break
            end = time.time() + backoff
            while time.time() < end and not stop_check():
                time.sleep(min(0.25, max(0.0, end - time.time())))
            backoff = min(a.retry_max_s, backoff * 2)
    finally:
        if _stop["why"] is None:
            _stop["why"] = "loop exit"
        try:
            os.close(fd)
        except OSError:
            pass
        after = os.path.getsize(rec_path) if os.path.exists(rec_path) else 0
        span = ((last_recv_ns - first_recv_ns) / 1e9) if (first_recv_ns and last_recv_ns) else None
        summary = {
            "out": os.path.abspath(a.out), "p3rec": os.path.abspath(rec_path), "url": a.url,
            "pid": os.getpid(), "nice": nice_now, "stopped": _stop["why"],
            "t_start": t_start, "t_end": time.time(), "wall_s": round(time.time() - t_start, 3),
            "packets": packets, "blob_bytes": blob_bytes,
            "packets_before": packets_before, "packets_total": packets_before + packets,
            "p3rec_bytes_before": before, "p3rec_bytes_after": after,
            "p3rec_bytes_written": after - before, "repaired_bytes": repaired,
            "prev_last_recv_s": (prev_last_ns / 1e9) if prev_last_ns else None,
            "seconds": round(span, 4) if span else None,
            "fps": round((packets - 1) / span, 4) if span and span > 0 else None,
            "bytes_per_s": round(blob_bytes / span, 1) if span and span > 0 else None,
            "first_recv_s": (first_recv_ns / 1e9) if first_recv_ns else None,
            "last_recv_s": (last_recv_ns / 1e9) if last_recv_ns else None,
            "first_recv_ns": first_recv_ns, "last_recv_ns": last_recv_ns,
            "connections": conns, "reconnects": max(0, conns - 1), "connect_failures": conn_fails,
            "gaps": gaps_n, "gap_s_total": round(gap_s_total, 4),
            "partial_frames_discarded": partial_n,
            # The wall clock is what every timestamp here uses, because the runner's launch times
            # use it too; the monotonic span is the witness that it did not step mid-session.
            "mono_s": round(mono_last - mono_first, 4) if (mono_first and mono_last) else None,
            "clock_steps": clock_steps, "locked": lock_fd is not None,
            "free_mb": free_mb(a.out), "stop_files": stops,
            "status_polls": poller.n if poller else 0,
            "status_failures": poller.fail if poller else 0,
            "status_last": poller.last if poller else None,
            "args": vars(a),
        }
        try:
            with open(os.path.join(a.out, "done.json"), "w") as f:
                json.dump(summary, f, indent=1)
        except OSError as e:
            say("done.json write failed: %s" % e)
        event("stop", **{k: summary[k] for k in
                         ("stopped", "packets", "blob_bytes", "seconds", "fps", "connections",
                          "reconnects", "connect_failures", "gaps", "gap_s_total",
                          "p3rec_bytes_before", "p3rec_bytes_after", "wall_s")})
        say("stop (%s): %d packets, %.0f MB, %s s, %s fps, %d reconnects, %d gaps (%.3f s), "
            "%d connect failures"
            % (_stop["why"], packets, blob_bytes / 1e6,
               ("%.1f" % span) if span else "?",
               ("%.2f" % summary["fps"]) if summary["fps"] else "?",
               summary["reconnects"], gaps_n, gap_s_total, conn_fails))
        gaps.close()
        log.close()
        if lock_fd is not None:        # the kernel would do this at exit; be explicit
            try:
                os.close(lock_fd)
            except OSError:
                pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
