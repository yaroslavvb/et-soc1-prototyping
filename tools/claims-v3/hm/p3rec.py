#!/usr/bin/env python3
"""p3rec.py - E62 heat movies: decode the thermal camera's recordings and live-stream captures.

One library for both capture shapes the experiment produces, plus a `summarize` CLI.
Pure standard library + numpy, so the same file runs on the lab host (python3.12 + numpy 1.26,
no matplotlib, no ffmpeg) and on the laptop.

Wire formats
------------
`/stream.raw.z` (the phone app's lossless stream, 25 fps, ~1.0 MB/s) is a bare repetition of

    uint32 LE compressed_len ; zlib(SCI packet of 99,392 B)

and nothing else: no HTTP chunking, no boundary, no trailer. A capture of it (what `curl -m N`
leaves behind) carries **no host timestamps**; a frame's only clocks are the phone's, inside the
header. Truncation mid-frame is the normal end of such a capture and stops the iterator cleanly.

`.p3rec` is the recording format `record_cam.py` writes, and the format the sensitivity experiments
already use:

    repeat { uint64 LE host_recv_ns ; uint32 LE len ; len bytes of the zlib blob exactly as received }

`host_recv_ns` is `time.time_ns()` on the recording host when the blob's last byte arrived. That is
the clock the runner's launch times use, so alignment needs no cross-machine offset. The phone's
`wall_ns` sits ~345 ms before the host receive time and that offset cannot be separated from the true
latency - never align compute events to `wall_ns`.

SCI packet (99,392 B) = 64 B header (magic `P3FZ`) + 1,024 B InfoLine (uint16[512], sensor rows
192-193) + 98,304 B thermal plane (256x192 uint16 LE, 1/64 K).

64-byte header, little endian after the magic
  off  0  4s   magic     "P3FZ" (compressed) / "P3FR" (uncompressed)
  off  4  u32  ver = 1
  off  8  i64  seq       +1 per frame on the phone. The drop detector
  off 16  i64  mono_ns   phone elapsedRealtimeNanos at USB parse (its good clock)
  off 24  i64  wall_ns   phone wall clock, ms resolution only
  off 32  i64  cnt1      firmware counter
  off 40  i64  cnt2      firmware counter
  off 48  i32  cnt3      firmware counter, wraps, not a frame index
  off 52  i16  w = 256
  off 54  i16  h = 192
  off 56  f32  fpa_c     focal-plane temperature, degC (0.0 when the telemetry read NaN)
  off 60  u8   gain      1 = high
  off 61  u8   auto_ffc  1 = automatic shutter enabled
  off 62  u16  reserved

Temperature
-----------
    degC = raw / 64 - 273.15        15.625 mK per count
Work in counts, or in mK via `to_mk`: the plane is linear in 1/64 K, so a difference of counts is a
difference in kelvin exactly. The emissivity correction is non-linear and is applied only by the
phone's `/frame.csv`, never to the stream - `celsius_corrected` is here for display parity only.
In the live `visualize` preset every count is a multiple of 4, i.e. the real step is 62.5 mK;
`summarize` measures that (`raw_step`) instead of assuming it.

API
---
    parse_header(buf)                  -> dict
    parse_packet(sci)                  -> (hdr, info uint16[512], plane uint16[192,256])
    parse_raw_packet(pkt)              -> same triple, for a 197,696 B P3FR packet
    to_sci(pkt)                        -> bytes, P3FR -> P3FZ (drops the AGC plane)

    iter_p3rec(path, planes=True)      -> yields (host_recv_ns, hdr, info, plane)
    iter_stream_file(path, ...)        -> yields (idx, hdr, info, plane)       # no timestamps
    iter_raw_file(path)                -> yields (idx, hdr, info, plane)
    iter_frames(path, kind="auto", planes=True)
                                       -> yields (t_ns_or_None, hdr, info, plane), either shape
    scan(path, kind="auto")            -> yields (t_ns_or_None, hdr, info)     # fast: no plane

Every iterator takes `on_error=<callable>`: it is handed a dict for each frame the file loses to
damage (`{kind, where, msg}`; kinds `zlib`, `frame`, `framing`, `truncated_tail`) instead of the
frame. Non-strict reading never raises on damage *after* the first good record - a damaged or
half-written tail costs the frames behind it and nothing else - but a first record that makes no
sense raises, so a file that is not a capture is still an error rather than an empty summary.

    celsius(plane) / to_mk(plane) / celsius_corrected(plane, e, t_ref) / info_temps(info)
    load_cube(path, kind="auto", max_frames=None) -> (uint16[n,192,256], [hdr], [info])
    summarize(path, kind="auto", fast=False, step_mk=20.0, step_stat="mean") -> dict
    ffc_events(path, ...)              -> the shutter events: each is a run of bit-identical planes,
                                          with the per-pixel step measured across it. A run whose
                                          `seq` repeats is a frame the *recording* holds twice, not
                                          a shutter: read `kind`, and use the `shutter` ones
    level_track(path, ..., stat="mean") -> the per-frame whole-frame level and its jumps (FFC
                                           candidates). Flag on the mean: in `visualize` the
                                           whole-frame *median* dithers by a full 62.5 mK quantum

`scan` is the fast path: it inflates only the first 1,088 bytes of each blob (header + InfoLine) and
skips the plane on disk, so a header-only pass over a 5-minute recording costs a few hundred
milliseconds instead of tens of seconds. Nothing here ever holds more than one plane at a time
except `load_cube`, which is for short captures only.

CLI
---
    python3 p3rec.py summarize <file> [--kind auto|z|p3rec|raw] [--fast] [--brief] [--step-mk 20]
                                      [--json out.json] [--npy cube.npy] [--quiet]
    python3 p3rec.py ffc <file> [--window 25] [--json out.json]   # the shutter events
    python3 p3rec.py steps <file> [--step-mk 20] [--stat mean|median] [--json out.json]

On the laptop: `uv run -q --with numpy python3 p3rec.py summarize cam.p3rec`.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import struct
import sys
import zlib

import numpy as np

W, H = 256, 192
HDR_SIZE = 64
INFO_WORDS = 512                                    # 1,024 bytes
PLANE_BYTES = W * H * 2                             # 98,304
SCI_SIZE = HDR_SIZE + 2 * INFO_WORDS + PLANE_BYTES  # 99,392
RAW_PACKET = HDR_SIZE + W * (2 * H + 2) * 2         # 197,696
HDR_FMT = "<4sIqqqqqihhfBBH"
assert struct.calcsize(HDR_FMT) == HDR_SIZE
PREFIX_BYTES = HDR_SIZE + 2 * INFO_WORDS            # 1,088: all `scan` needs out of a blob

TEMP_SCALE = 64.0
KELVIN_OFFSET = 273.15
MK_PER_LSB = 1000.0 / TEMP_SCALE                    # 15.625 mK
MAX_BLOB = 1_000_000                                # a compressed frame is ~40 KB; this is the sanity bound

# InfoLine word indices (uint16 index into the 512-word InfoLine). The sensor's own map is
# THERMAL_MASTER_P3.md section 5.1; where its label and this capture disagree, both are recorded.
INFO_FRAMECOUNT = 64     # ISP frame counter, +1 per frame with no jitter
INFO_VTEMP = 65          # raw 14-bit FPA thermistor ADC; falls as the focal plane warms
INFO_MEAN_Y16 = 68       # the map calls this 4 x word 176, a scene mean in 1/64 K. Measured on the
                         # live camera it is neither: word 68 / 4 - word 176 = -210..-213 counts,
                         # and it correlates 0.27 with the plane mean. An AGC-domain number
INFO_FFC_COUNTDOWN = 21  # ffcCountdown lives in byte 42 = word 21, low byte (0 when auto-FFC is off)
INFO_T16_168 = 168       # 1/16 K. The map: Y14 scene min. Measured: 34.73-34.91 degC, steady
INFO_T16_174 = 174       # 1/16 K. The map: unfiltered Y14 scene max. Measured: 45.47-45.73 degC
INFO_T16_176 = 176       # 1/16 K. The map: Y14 scene mean. Measured: equal to the header's fpa_c to
                         # within one count (0.0625 degC) in every frame of two captures, while the
                         # plane mean is 3.5 degC away - so here it tracks the focal plane
INFO_FRAMECNT = 180      # VSYNC frame counter, also +1 per frame
# The names the camera reader's decoder used, kept so its scripts still import.
INFO_SHUTTER_T16, INFO_LENS_T16, INFO_FPA_T16 = INFO_T16_168, INFO_T16_174, INFO_T16_176

_REC = struct.Struct("<QI")          # .p3rec record header: host_recv_ns, len
_LEN = struct.Struct("<I")           # /stream.raw.z length prefix


# --------------------------------------------------------------------------------------- parsing

def parse_header(buf) -> dict:
    """The 64-byte packet header -> dict. Accepts bytes or a memoryview of at least 64 bytes."""
    h = struct.unpack(HDR_FMT, bytes(buf[:HDR_SIZE]))
    return dict(magic=h[0].decode("latin1"), ver=h[1], seq=h[2], mono_ns=h[3], wall_ns=h[4],
                cnt1=h[5], cnt2=h[6], cnt3=h[7], w=h[8], h=h[9], fpa_c=h[10],
                gain=h[11], auto_ffc=h[12])


def parse_packet(sci: bytes):
    """Decompressed P3FZ packet (99,392 B) -> (hdr, InfoLine uint16[512], plane uint16[192,256]).

    The returned arrays are views on `sci` and are therefore read-only; copy before writing.
    """
    if len(sci) != SCI_SIZE:
        raise ValueError("expected %d bytes, got %d" % (SCI_SIZE, len(sci)))
    hdr = parse_header(sci)
    info = np.frombuffer(sci, dtype="<u2", count=INFO_WORDS, offset=HDR_SIZE)
    plane = np.frombuffer(sci, dtype="<u2", count=W * H,
                          offset=HDR_SIZE + 2 * INFO_WORDS).reshape(H, W)
    return hdr, info, plane


def parse_prefix(prefix: bytes):
    """The first 1,088 bytes of an SCI packet -> (hdr, InfoLine uint16[512]). What `scan` uses."""
    if len(prefix) < PREFIX_BYTES:
        raise ValueError("expected %d bytes, got %d" % (PREFIX_BYTES, len(prefix)))
    return parse_header(prefix), np.frombuffer(prefix, dtype="<u2", count=INFO_WORDS, offset=HDR_SIZE)


def parse_raw_packet(pkt: bytes):
    """One 197,696-byte P3FR packet (/frame.raw, /stream.raw) -> (hdr, info, plane).

    Layout after the header: 192 rows of 8-bit AGC stored as uint16, then the 2 InfoLine rows,
    then the 192 thermal rows.
    """
    if len(pkt) != RAW_PACKET:
        raise ValueError("expected %d bytes, got %d" % (RAW_PACKET, len(pkt)))
    hdr = parse_header(pkt)
    info = np.frombuffer(pkt, dtype="<u2", count=INFO_WORDS, offset=HDR_SIZE + PLANE_BYTES)
    plane = np.frombuffer(pkt, dtype="<u2", count=W * H,
                          offset=HDR_SIZE + PLANE_BYTES + 2 * INFO_WORDS).reshape(H, W)
    return hdr, info, plane


def to_sci(pkt: bytes) -> bytes:
    """P3FR raw packet -> the equivalent P3FZ SCI packet (drops the AGC plane)."""
    return pkt[:3] + b"Z" + pkt[4:HDR_SIZE] + pkt[HDR_SIZE + PLANE_BYTES:]


# ----------------------------------------------------------------------------------- temperature

def celsius(plane) -> np.ndarray:
    """raw 1/64 K counts -> degC (emissivity 1, the stream's own scale)."""
    return np.asarray(plane, dtype=np.float32) / TEMP_SCALE - KELVIN_OFFSET


def to_mk(plane) -> np.ndarray:
    """raw counts -> millikelvin, linear and offset-free under differencing. The analysis unit."""
    return np.asarray(plane, dtype=np.float32) * MK_PER_LSB


def celsius_corrected(plane, emissivity: float = 1.0, reflected_c: float = 25.0) -> np.ndarray:
    """The phone's grey-body correction (what `/frame.csv` bakes in). Display parity only.

    Non-linear in the raw count, so never difference these. The live camera is set to
    emissivity 0.960, reflected 25.0 degC.
    """
    if emissivity >= 0.999 or emissivity <= 0.01:
        return celsius(plane)
    t_app = np.asarray(plane, dtype=np.float64) / TEMP_SCALE
    t_ref = reflected_c + KELVIN_OFFSET
    t4 = (t_app ** 4 - (1.0 - emissivity) * t_ref ** 4) / emissivity
    out = np.where(t4 > 0, np.power(np.maximum(t4, 1e-9), 0.25) - KELVIN_OFFSET, t_app - KELVIN_OFFSET)
    return out.astype(np.float32)


def info_temps(info) -> dict:
    """InfoLine 1/16-K words -> degC, NaN outside the app's 3200..6400 sanity window.

    The three temperature words are reported **by word index**, because what they mean is not
    settled: the sensor's published map (THERMAL_MASTER_P3.md 5.1) calls word 176 the Y14 scene
    mean, 174 the unfiltered scene max and 168 the scene min, but on this camera word 176 equals
    the header's own `fpa_c` to within one count in every frame measured while the plane mean sits
    3.5 degC away. `fpa_c`, `lens_c` and `shutter_c` are kept as aliases of 176 / 174 / 168 for the
    scripts that already use them; prefer the header's `fpa_c` for the focal plane, and don't quote
    any of these three as a lens or shutter temperature without checking.
    """
    def t16(i):
        v = int(info[i])
        return v / 16.0 - KELVIN_OFFSET if 3200 <= v <= 6400 else float("nan")
    t176, t174, t168 = t16(INFO_T16_176), t16(INFO_T16_174), t16(INFO_T16_168)
    return dict(w176_c=t176, w174_c=t174, w168_c=t168,
                fpa_c=t176, lens_c=t174, shutter_c=t168,
                vtemp_adc=int(info[INFO_VTEMP]),
                mean_c=int(info[INFO_MEAN_Y16]) / TEMP_SCALE - KELVIN_OFFSET,
                ffc_countdown=int(info[INFO_FFC_COUNTDOWN]) & 0xFF,
                framecount=int(info[INFO_FRAMECOUNT]), framecnt=int(info[INFO_FRAMECNT]))


# ------------------------------------------------------------------------------------- iterators

def _inflate(blob: bytes, want: int | None = None) -> bytes:
    """Inflate `blob`, stopping once `want` bytes are out (None = all of it)."""
    if want is None:
        return zlib.decompress(blob)
    return zlib.decompressobj().decompress(blob, want)


def _note(on_error, kind: str, where: str, msg: str) -> None:
    """Report one lost frame to the caller's collector, or to stderr if there is none.

    A truncated tail is the normal end of a `curl -m N` capture, so with no collector it stays
    quiet; real damage is worth a line on stderr.
    """
    if on_error is not None:
        on_error({"kind": kind, "where": where, "msg": msg})
    elif kind != "truncated_tail":
        print("p3rec: %s at %s: %s" % (kind, where, msg), file=sys.stderr)


def _decode(buf: bytes, want: int | None):
    """(hdr, info, plane) from an inflated blob; `want` set means header + InfoLine only."""
    if want is None:
        return parse_packet(buf)
    hdr, info = parse_prefix(buf)
    return hdr, info, None


def iter_p3rec(path: str, planes: bool = True, strict: bool = False, on_error=None):
    """Yield (host_recv_ns, hdr, info, plane) from a .p3rec recording, oldest first.

    With planes=False the plane is None and only the first 1,088 bytes of each blob are inflated
    (the rest is skipped on disk) - the fast header pass.

    Damage tolerance, non-strict (the default): a truncated tail - what a killed recorder leaves -
    ends the iteration, and so does a record header whose length field is garbage, which is what a
    disk-full tear leaves; both are reported through `on_error` and the frames already read are
    still yielded. A corrupt blob in the middle costs that one frame. The *first* record is the
    exception: if its length field is impossible the file is not a .p3rec at all and ValueError is
    raised. strict=True raises on every one of these.
    """
    want = None if planes else PREFIX_BYTES
    nrec = 0
    with open(path, "rb") as f:
        while True:
            hb = f.read(_REC.size)
            if len(hb) < _REC.size:
                if hb:
                    msg = "truncated record header at offset %d" % (f.tell() - len(hb))
                    if strict:
                        raise EOFError(msg)
                    _note(on_error, "truncated_tail", "record %d" % nrec, msg)
                return
            recv_ns, n = _REC.unpack(hb)
            if not 0 < n < MAX_BLOB:
                msg = "bad blob length %d at offset %d" % (n, f.tell() - 4)
                if strict or nrec == 0:
                    raise ValueError(msg)
                _note(on_error, "framing", "record %d" % nrec, msg)
                return
            take = n if want is None else min(n, 65536)
            blob = f.read(take)
            if len(blob) < take:
                msg = "truncated blob at offset %d (wanted %d B)" % (f.tell(), take)
                if strict:
                    raise EOFError(msg)
                _note(on_error, "truncated_tail", "record %d" % nrec, msg)
                return
            if take < n:
                f.seek(n - take, os.SEEK_CUR)
            try:
                hdr, info, plane = _decode(_inflate(blob, want), want)
            except (zlib.error, ValueError) as e:
                if strict:
                    raise
                _note(on_error, "zlib" if isinstance(e, zlib.error) else "frame",
                      "record %d" % nrec, str(e))
                nrec += 1
                continue
            nrec += 1
            yield recv_ns, hdr, info, plane


def iter_stream_file(path: str, strict: bool = False, planes: bool = True, on_error=None):
    """Yield (idx, hdr, info, plane) from a raw capture of /stream.raw.z. No host timestamps.

    A capture cut off mid-frame (the normal end of `curl -m N`) just stops. Damage is tolerated
    exactly as in `iter_p3rec`: reported through `on_error`, fatal only in the first frame or with
    strict=True.
    """
    want = None if planes else PREFIX_BYTES
    idx = 0
    with open(path, "rb") as f:
        while True:
            lb = f.read(_LEN.size)
            if len(lb) < _LEN.size:
                if lb:
                    msg = "truncated length prefix at frame %d" % idx
                    if strict:
                        raise EOFError(msg)
                    _note(on_error, "truncated_tail", "frame %d" % idx, msg)
                return
            (clen,) = _LEN.unpack(lb)
            if not 0 < clen < MAX_BLOB:
                msg = "bad frame length %d at offset %d" % (clen, f.tell() - 4)
                if strict or idx == 0:
                    raise ValueError(msg)
                _note(on_error, "framing", "frame %d" % idx, msg)
                return
            take = clen if want is None else min(clen, 65536)
            blob = f.read(take)
            if len(blob) < take:
                msg = "truncated frame %d at offset %d" % (idx, f.tell())
                if strict:
                    raise EOFError(msg)
                _note(on_error, "truncated_tail", "frame %d" % idx, msg)
                return
            if take < clen:
                f.seek(clen - take, os.SEEK_CUR)
            try:
                hdr, info, plane = _decode(_inflate(blob, want), want)
            except (zlib.error, ValueError) as e:
                if strict:
                    raise
                _note(on_error, "zlib" if isinstance(e, zlib.error) else "frame",
                      "frame %d" % idx, str(e))
                idx += 1
                continue
            yield idx, hdr, info, plane
            idx += 1


def iter_raw_file(path: str):
    """Yield (idx, hdr, info, plane) from a /stream.raw or /frame.raw dump (uncompressed P3FR)."""
    idx = 0
    with open(path, "rb") as f:
        while True:
            pkt = f.read(RAW_PACKET)
            if len(pkt) < RAW_PACKET:
                return
            if pkt[:4] != b"P3FR":
                raise ValueError("bad magic %r at packet %d" % (pkt[:4], idx))
            yield (idx,) + parse_raw_packet(pkt)
            idx += 1


def _zlib_header(buf: bytes, off: int) -> bool:
    """Do the two bytes at `off` start a zlib stream? (CM = 8 and the check word divides 31.)

    Every blob in both capture shapes is a zlib stream, and its first two bytes sit at a fixed
    offset: 4 in a /stream.raw.z capture, 12 in a .p3rec. That makes the two shapes tell themselves
    apart deterministically instead of by a guess about the first 12 bytes.
    """
    if len(buf) < off + 2:
        return False
    cmf, flg = buf[off], buf[off + 1]
    return (cmf & 0x0F) == 8 and ((cmf << 8) | flg) % 31 == 0


def guess_kind(path: str) -> str:
    """'p3rec', 'z' or 'raw', from the suffix first and the framing of the first record as the
    tiebreak: a plausible length *and* a zlib header where that shape puts it."""
    low = path.lower()
    if low.endswith(".p3rec"):
        return "p3rec"
    if low.endswith(".raw") or low.endswith(".p3fr"):
        return "raw"
    try:
        with open(path, "rb") as f:
            head = f.read(24)
    except OSError:
        return "z"
    if head[:4] == b"P3FR":
        return "raw"
    z_ok = p_ok = False
    if len(head) >= 6:
        (clen,) = _LEN.unpack(head[:4])
        z_ok = 0 < clen < MAX_BLOB and _zlib_header(head, _LEN.size)
    if len(head) >= 14:
        # .p3rec: a plausible epoch-ns u64, then a u32 length, then the blob.
        recv_ns, n = _REC.unpack(head[:12])
        p_ok = (1_000_000_000_000_000_000 < recv_ns < 3_000_000_000_000_000_000
                and 0 < n < MAX_BLOB and _zlib_header(head, _REC.size))
    if p_ok and not z_ok:
        return "p3rec"
    if z_ok and not p_ok:
        return "z"
    if len(head) >= 16:                   # neither or both: fall back to the old guess
        recv_ns, n = _REC.unpack(head[:12])
        if 1_000_000_000_000_000_000 < recv_ns < 3_000_000_000_000_000_000 and 0 < n < MAX_BLOB:
            return "p3rec"
    return "z"


def iter_frames(path: str, kind: str = "auto", planes: bool = True, strict: bool = False,
                on_error=None):
    """One iterator over either capture shape: yields (t_ns_or_None, hdr, info, plane).

    t_ns is the host receive time for a .p3rec and None for a capture that carries no host clock
    (use hdr['mono_ns'] then). This is the entry point the reduction should use.
    """
    if kind == "auto":
        kind = guess_kind(path)
    if kind == "p3rec":
        for recv_ns, hdr, info, plane in iter_p3rec(path, planes=planes, strict=strict,
                                                    on_error=on_error):
            yield recv_ns, hdr, info, plane
    elif kind == "z":
        for _idx, hdr, info, plane in iter_stream_file(path, strict=strict, planes=planes,
                                                       on_error=on_error):
            yield None, hdr, info, plane
    elif kind == "raw":
        for _idx, hdr, info, plane in iter_raw_file(path):
            yield None, hdr, info, plane
    else:
        raise ValueError("unknown kind %r" % kind)


def scan(path: str, kind: str = "auto", strict: bool = False, on_error=None):
    """Fast header pass: yields (t_ns_or_None, hdr, info) and never decodes a plane."""
    for t_ns, hdr, info, _plane in iter_frames(path, kind=kind, planes=False, strict=strict,
                                               on_error=on_error):
        yield t_ns, hdr, info


def load_cube(path: str, kind: str = "auto", max_frames: int | None = None):
    """Whole capture -> (cube uint16[n,192,256], [hdr], [info]). Short captures only: 98 KB a frame."""
    planes, hdrs, infos = [], [], []
    for _t, hdr, info, plane in iter_frames(path, kind=kind):
        planes.append(plane.copy())
        hdrs.append(hdr)
        infos.append(np.array(info))
        if max_frames and len(planes) >= max_frames:
            break
    cube = np.stack(planes) if planes else np.zeros((0, H, W), "<u2")
    return cube, hdrs, infos


# -------------------------------------------------------------------------------------- analysis

def _fps(n: int, span_s: float) -> float | None:
    return round((n - 1) / span_s, 4) if n > 1 and span_s > 0 else None


def _seq_report(seqs: np.ndarray, times_s: np.ndarray | None, max_list: int = 50) -> dict:
    """Sequence contiguity: how many frames the camera made that this file does not hold.

    `seq` is the phone's own frame counter and normally steps by exactly 1, but two things break
    that and they must not be confused with a loss:

    * **a repeat** (step 0). The phone serves the newest frame and keeps its `lastSeq` per
      connection, so a reconnect inside one frame time can re-serve a frame already recorded; two
      recorders appending to one file do the same thing wholesale.
    * **a step backwards** (step < 0), which is the phone app restarting its counter.

    Counting either as "dropped" is what `(last - first + 1) - n` does, and it goes *negative* on a
    repeat. So `dropped_by_seq` here is the sum of the forward gaps only (identical to the old
    formula on a monotone sequence), and repeats and backward steps get their own counts. Every
    listed gap carries a `kind`, and `missed` is never negative.
    """
    out = {"seq_first": None, "seq_last": None, "seq_contiguous": None, "seq_monotonic": None,
           "dropped_by_seq": 0, "n_seq_gaps": 0, "n_seq_dups": 0, "n_seq_backwards": 0,
           "seq_gaps": []}
    if len(seqs) == 0:
        return out
    d = np.diff(seqs)
    bad = np.nonzero(d != 1)[0]
    gaps = []
    for i in bad[:max_list]:
        step = int(d[i])
        g = {"index": int(i), "seq": int(seqs[i]), "next_seq": int(seqs[i + 1]),
             "seq_step": step, "missed": max(0, step - 1),
             "kind": "missed" if step > 1 else ("repeat" if step == 0 else "backwards")}
        if times_s is not None:
            g["t_s"] = round(float(times_s[i]), 4)
            g["dt_s"] = round(float(times_s[i + 1] - times_s[i]), 4)
        gaps.append(g)
    fwd = d[d > 1]
    out.update(seq_first=int(seqs[0]), seq_last=int(seqs[-1]),
               seq_contiguous=bool(np.all(d == 1)) if len(seqs) > 1 else None,
               seq_monotonic=bool(np.all(d > 0)) if len(seqs) > 1 else None,
               dropped_by_seq=int(fwd.sum() - fwd.size),
               n_seq_gaps=int(np.sum(d > 1)), n_seq_dups=int(np.sum(d == 0)),
               n_seq_backwards=int(np.sum(d < 0)), seq_gaps=gaps)
    return out


def _raw_step(values: np.ndarray) -> int | None:
    """The real quantisation step in counts: gcd of the gaps between the distinct values seen.

    The container is 1/64 K (15.625 mK) but the live `visualize` preset rounds to multiples of 4
    counts (62.5 mK). This measures which it is instead of assuming.
    """
    v = np.unique(values)
    if v.size < 3:
        return None
    g = 0
    for d in np.diff(v.astype(np.int64)):
        g = math.gcd(g, int(d))
        if g == 1:
            break
    return int(g) if g else None


def level_track(path: str, kind: str = "auto", step_mk: float = 20.0, stat: str = "mean",
                sub_px: int = 4):
    """Per-frame whole-frame level (mK), both as the mean and as the median, and its jumps.

    A jump in the whole-frame level is the visible signature of a flat-field correction (FFC /
    shutter): the offset map is replaced in one frame. Jumps are flagged on `stat`.

    **Use the mean, not the median.** In the live `visualize` preset every count is a multiple of 4
    (62.5 mK), so a whole-frame median lands on that lattice and dithers by a whole quantum between
    neighbouring frames: measured on a 15 s idle capture the median took 3 distinct values in 375
    frames and crossed a 20 mK threshold 31 times with no FFC anywhere in the file. The mean of the
    49,152 pixels averages the quantisation away - the same capture gives a median |step| of 0.9 mK
    and a maximum of 18.6 mK. `stat="median"` is kept because it is cheap to ask for, not because it
    works at this threshold.

    `sub_px` subsamples the plane for the median only (every 4th row and column = 3,072 pixels);
    the mean always uses every pixel. Returns dict(t_s, seq, mean_mk, median_mk, dup, jumps, ...).
    `dup` marks a frame whose plane is bit-identical to the one before it - the stream should never
    do that (the phone serves the newest frame and skips rather than queueing), so a run of `dup`
    frames is a frozen sensor, which is what the mechanical shutter looks like if it stalls.
    """
    if stat not in ("mean", "median"):
        raise ValueError("stat must be 'mean' or 'median', got %r" % (stat,))
    t_ns, seqs, mean, med, dup, fpa = [], [], [], [], [], []
    prev = None
    for t, hdr, _info, plane in iter_frames(path, kind=kind):
        mean.append(float(plane.mean()) * MK_PER_LSB)
        med.append(float(np.median(plane[::sub_px, ::sub_px])) * MK_PER_LSB)
        dup.append(prev is not None and bool(np.array_equal(plane, prev)))
        prev = plane.copy()
        seqs.append(int(hdr["seq"]))
        fpa.append(float(hdr["fpa_c"]))
        t_ns.append(t if t is not None else hdr["mono_ns"])
    n = len(mean)
    mean = np.asarray(mean, dtype=np.float64)
    med = np.asarray(med, dtype=np.float64)
    seqs = np.asarray(seqs, dtype=np.int64)
    dup = np.asarray(dup, dtype=bool)
    t0 = t_ns[0] if n else 0
    t_s = np.asarray([(t - t0) / 1e9 for t in t_ns], dtype=np.float64)
    lvl = mean if stat == "mean" else med
    jumps = []
    if n > 1:
        d = np.diff(lvl)
        for i in np.nonzero(np.abs(d) > step_mk)[0]:
            lo, hi = max(0, i - 12), min(n, i + 14)       # about +-0.5 s at 25 fps
            jumps.append({
                "index": int(i + 1), "t_s": round(float(t_s[i + 1]), 4), "seq": int(seqs[i + 1]),
                "step_mk": round(float(d[i]), 2),
                "mk_before": round(float(lvl[i]), 2), "mk_after": round(float(lvl[i + 1]), 2),
                "mean_step_mk": round(float(mean[i + 1] - mean[i]), 2),
                "median_step_mk": round(float(med[i + 1] - med[i]), 2),
                "seq_jump": int(seqs[i + 1] - seqs[i]),
                "dt_s": round(float(t_s[i + 1] - t_s[i]), 4),
                "dup_frames_within_0p5s": int(dup[lo:hi].sum()),
                "fpa_c": round(float(fpa[i + 1]), 3),
            })
    return {"n": n, "t_s": t_s, "seq": seqs, "mean_mk": mean, "median_mk": med, "dup": dup,
            "stat": stat, "step_mk_threshold": step_mk, "sub_px": sub_px, "jumps": jumps,
            "n_dup_frames": int(dup.sum()),
            "longest_dup_run": _longest_run(dup),
            "mean_mk_ptp": round(float(np.ptp(mean)), 2) if n else None,
            "median_mk_ptp": round(float(np.ptp(med)), 2) if n else None,
            "max_abs_mean_step_mk": round(float(np.max(np.abs(np.diff(mean)))), 2) if n > 1 else None,
            "max_abs_median_step_mk": round(float(np.max(np.abs(np.diff(med)))), 2) if n > 1 else None}


def median_track(path: str, kind: str = "auto", step_mk: float = 20.0, sub_px: int = 4):
    """`level_track` with stat='median'. See the warning there: the median dithers by 62.5 mK."""
    return level_track(path, kind=kind, step_mk=step_mk, stat="median", sub_px=sub_px)


def _longest_run(flags) -> int:
    best = cur = 0
    for v in flags:
        cur = cur + 1 if v else 0
        best = max(best, cur)
    return int(best)


BRIEF_ROWS = (
    ("packets", "packets"), ("bytes", "bytes"), ("kind", "kind"),
    ("recv_span_s", "span from host recv (s)"), ("mono_span_s", "span from phone mono (s)"),
    ("fps_recv", "fps, host receive times"), ("fps_seq", "fps, from seq over the span"),
    ("fps_mono", "fps, phone mono clock"),
    ("recv_dt_ms_median", "frame gap, host (ms, median)"),
    ("recv_dt_ms_max", "frame gap, host (ms, max)"),
    ("n_recv_backwards", "host clock stepped back (frames)"),
    ("seq_first", "seq first"), ("seq_last", "seq last"),
    ("seq_contiguous", "seq contiguous"), ("dropped_by_seq", "frames dropped (by seq)"),
    ("n_seq_gaps", "seq gaps"), ("n_seq_dups", "seq repeated (frame recorded twice)"),
    ("n_seq_backwards", "seq stepped backwards"),
    ("decode_errors", "frames lost to damage"), ("truncated_tail", "ends mid-record"),
    ("framecount_contiguous", "InfoLine framecount contiguous"),
    ("framecount_stalls", "sensor frame served twice (stalls)"),
    ("framecount_skips", "sensor frames never served (gaps)"),
    ("framecount_missed", "sensor frames missed in those gaps"),
    ("gain_values", "gain"), ("auto_ffc_values", "auto_ffc"),
    ("ffc_countdown_values", "InfoLine ffcCountdown"),
    ("fpa_c_first", "fpa_c first (degC)"), ("fpa_c_last", "fpa_c last (degC)"),
    ("fpa_c_range", "fpa_c range (degC)"),
    ("plane_min_c", "plane min (degC)"), ("plane_max_c", "plane max (degC)"),
    ("raw_step", "raw quantum (counts)"),
    ("mean_mk_ptp", "frame mean, peak to peak (mK)"),
    ("max_abs_mean_step_mk", "largest frame-to-frame mean step (mK)"),
    ("max_abs_median_step_mk", "largest frame-to-frame median step (mK)"),
    ("n_level_steps", "steps over the threshold (mean)"),
    ("n_median_steps", "steps over the threshold (median)"),
    ("dup_frames", "frozen frames (plane repeated)"),
    ("longest_dup_run", "longest frozen run (frames)"),
    ("n_ffc_runs", "shutter (FFC) events"),
    ("bytes_per_s", "bytes/s"), ("mean_compressed_frame_bytes", "mean compressed frame (B)"),
)


def brief(s: dict) -> str:
    """`summarize`'s dict as a one-screen table."""
    lines = ["%-38s %s" % (label, json.dumps(s[key])) for key, label in BRIEF_ROWS if key in s]
    for g in s.get("seq_gaps", [])[:10]:
        lines.append("  seq %s at t=%.3f s: %d -> %d, %d frames missed over %.3f s"
                     % (g.get("kind", "gap"), g.get("t_s", float("nan")), g["seq"], g["next_seq"],
                        g["missed"], g.get("dt_s", float("nan"))))
    for g in s.get("recv_gaps_over_1s", [])[:10]:
        lines.append("  host receive gap at t=%.3f s: %.3f s" % (g["t_s"], g["dt_s"]))
    for e in s.get("decode_error_list", [])[:10]:
        lines.append("  lost a frame (%s) at %s: %s" % (e["kind"], e["where"], e["msg"]))
    for r in s.get("dup_runs", [])[:20]:
        lines.append("  identical planes at t=%.3f s (seq %d): %d frames = %.2f s, "
                     "seq +%d, framecount +%d -> %s, level step %s mK"
                     % (r["t_s"], r["seq"], r["frames"], r["seconds"], r["seq_advance"],
                        r["framecount_advance"], r["kind"], json.dumps(r["level_step_mk"])))
    if not s.get("dup_runs"):
        for r in s.get("framecount_stall_runs", [])[:20]:
            lines.append("  sensor frame repeated at t=%.3f s (seq %d): %d frames = %.2f s "
                         "(the shutter, from the headers alone)"
                         % (r["t_s"], r["seq"], r["frames"], r["seconds"]))
    return "\n".join(lines)


def ffc_events(path: str, kind: str = "auto", window: int = 25, min_run: int = 2):
    """The shutter (FFC) events in a capture, found by the only signature that is unambiguous.

    **What an FFC looks like in this stream, measured on a 5-minute idle capture.** The plane goes
    bit-identical for exactly 18 frames (0.72 s, the documented 350-500 ms mechanical actuation plus
    settling) while `seq` keeps advancing - so an FFC is *not* a sequence gap and leaves no hole in
    the recording. Coming out of it the whole offset map has been replaced: the per-pixel step was
    +32, +305 and -100 mK (median) at the three events, with 410-590 mK of spread across the frame
    and a clear gradient. Bridging an FFC with one scalar would leave hundreds of mK of false
    spatial structure - the size of the effect E62 is looking for - so the bridge is per pixel.

    The whole-frame level is useless as the detector: in the `visualize` preset every count is a
    multiple of 4, so when the field drifts, two thirds of the pixels cross a lattice boundary in
    the same frame and the frame mean dithers by 25-70 mK with no physical cause (10.9% of frames
    crossed 20 mK in that capture, 0 of them FFCs). Hence `dup`, not `step_mk`.

    **A frozen run is not always the shutter.** Identical planes also appear when the *recording*
    holds a frame twice - a reconnect inside one frame time, or two recorders appending to one file.
    The two are told apart by the headers: through a shutter `seq` keeps stepping by 1 while the
    sensor's InfoLine framecount stalls, whereas a duplicated record repeats `seq` as well. Each
    event carries `seq_advance`, `framecount_advance` and a `kind` of `shutter`,
    `duplicate_records` or `unclear`; only `shutter` events are the camera's own.

    One pass, holding a ring of `window` planes. Each event gets the per-pixel step between the
    `window` frames before the freeze and the `window` after it:
    `[{index, t_s, seq, frames, repeats, seconds, kind, step_mk_median, step_mk_p95, ...}]`.
    `index` is the first frame of the identical run (it still carries the pre-shutter picture) and
    `frames` counts every identical frame, so `frames = repeats + 1`.
    """
    from collections import deque
    ring: deque = deque(maxlen=window)   # the last `window` distinct planes, float32
    times: list = []                     # (t_ns, seq, framecount) per frame index
    events: list = []
    prev = None
    run_len = 0
    pre_snapshot: list = []
    pending = None                        # a freeze waiting for its post-freeze frames
    post: list = []
    for i, (t_ns, hdr, info, plane) in enumerate(iter_frames(path, kind=kind)):
        times.append((t_ns if t_ns is not None else hdr["mono_ns"], int(hdr["seq"]),
                      int(info[INFO_FRAMECOUNT])))
        same = prev is not None and np.array_equal(plane, prev)
        prev = plane
        if same:
            if run_len == 0:
                pre_snapshot = list(ring)
            run_len += 1
            continue
        if run_len >= min_run:            # the freeze ended with this frame
            if pending is not None:       # another freeze before the last one got its window
                events.append(_ffc_step(pending, post))
            pending = {"index": i - run_len - 1, "repeats": run_len, "pre": pre_snapshot}
            post = []
        run_len = 0
        f = plane.astype(np.float32)
        if pending is not None:
            post.append(f)
            if len(post) >= window:
                events.append(_ffc_step(pending, post))
                pending, post = None, []
        ring.append(f)
    if run_len >= min_run:                # the capture ended inside a freeze
        events.append(_ffc_step({"index": len(times) - run_len - 1, "repeats": run_len,
                                 "pre": pre_snapshot}, None))
    elif pending is not None:
        events.append(_ffc_step(pending, post))
    if times:
        t0 = times[0][0]
        for ev in events:
            a = max(0, min(ev["index"], len(times) - 1))
            b = min(a + ev["repeats"], len(times) - 1)
            t_ns, seq, fc = times[a]
            ev["t_s"] = round((t_ns - t0) / 1e9, 4)
            ev["t_host_s"] = t_ns / 1e9
            ev["seq"] = seq
            ev["seconds"] = round((times[b][0] - t_ns) / 1e9, 4)
            ev["seq_advance"] = times[b][1] - seq
            ev["framecount_advance"] = (times[b][2] - fc) % 65536
            ev["kind"] = ("shutter" if ev["seq_advance"] == ev["repeats"]
                                       and ev["framecount_advance"] == 0
                          else "duplicate_records" if ev["seq_advance"] == 0
                          else "unclear")
    for k in range(1, len(events)):
        events[k]["since_previous_s"] = round(events[k]["t_s"] - events[k - 1]["t_s"], 4)
    return events


def _ffc_step(ev: dict, post) -> dict:
    """One event record: the freeze plus the per-pixel step between the frames either side of it."""
    pre = ev.pop("pre", None)
    rec = {"index": ev["index"], "frames": ev["repeats"] + 1, "repeats": ev["repeats"],
           "seconds": round(ev["repeats"] / 25.0, 4), "kind": None, "seq_advance": None,
           "framecount_advance": None,
           "t_s": None, "t_host_s": None, "seq": None, "n_pre": len(pre or []),
           "n_post": len(post or []), "method": "frozen_plane_run"}
    if pre and post:
        step = (np.mean(np.stack(post), axis=0) - np.mean(np.stack(pre), axis=0)) * MK_PER_LSB
        rec.update(step_mk_median=round(float(np.median(step)), 2),
                   step_mk_mean=round(float(step.mean()), 2),
                   step_mk_p5=round(float(np.percentile(step, 5)), 2),
                   step_mk_p95=round(float(np.percentile(step, 95)), 2),
                   step_mk_ptp=round(float(np.ptp(step)), 2))
    else:
        rec.update(step_mk_median=None, step_mk_mean=None, step_mk_p5=None, step_mk_p95=None,
                   step_mk_ptp=None,
                   note="not enough frames on one side of the freeze to measure the step")
    return rec


def summarize(path: str, kind: str = "auto", fast: bool = False, step_mk: float = 20.0,
              max_gaps: int = 50, step_stat: str = "mean") -> dict:
    """Everything one wants to know about a capture, in one streaming pass (never stacks planes).

    fast=True skips the planes entirely (no degrees, no FFC candidates) and runs ~50x quicker.
    `step_stat` picks the level used to flag FFC candidates: 'mean' (the only one that works at a
    20 mK threshold - see `level_track`) or 'median'.

    Damage is counted, not fatal: `decode_errors` is the number of frames lost to a corrupt blob or
    broken framing, `decode_error_list` the first few with their offsets, and `truncated_tail` says
    the file ends mid-record (normal for `curl -m N`, a killed recorder otherwise).
    """
    if kind == "auto":
        kind = guess_kind(path)
    out: dict = {"file": os.path.abspath(path), "kind": kind, "fast": bool(fast), "packets": 0}
    try:
        out["bytes"] = os.path.getsize(path)
    except OSError:
        out["bytes"] = None

    if step_stat not in ("mean", "median"):
        raise ValueError("step_stat must be 'mean' or 'median', got %r" % (step_stat,))
    errs: list = []

    def on_error(rec):
        errs.append(rec)
    recv, mono, wall, seqs, fpa, auto_ffc, gain, framecount, ffc_cd = [], [], [], [], [], set(), set(), [], set()
    raw_min, raw_max = None, None
    frame_med, frame_mean = [], []
    dup_n = 0
    dup_flags = []
    prev_plane = None
    uniq: set[int] = set()
    hdr0 = info0 = infoN = None
    n = 0
    for t_ns, hdr, info, plane in iter_frames(path, kind=kind, planes=not fast, on_error=on_error):
        n += 1
        if hdr0 is None:
            hdr0, info0 = hdr, np.array(info)
        infoN = info
        recv.append(t_ns)
        mono.append(hdr["mono_ns"])
        wall.append(hdr["wall_ns"])
        seqs.append(hdr["seq"])
        fpa.append(float(hdr["fpa_c"]))
        auto_ffc.add(int(hdr["auto_ffc"]))
        gain.add(int(hdr["gain"]))
        framecount.append(int(info[INFO_FRAMECOUNT]))
        ffc_cd.add(int(info[INFO_FFC_COUNTDOWN]) & 0xFF)
        if plane is not None:
            lo, hi = int(plane.min()), int(plane.max())
            raw_min = lo if raw_min is None else min(raw_min, lo)
            raw_max = hi if raw_max is None else max(raw_max, hi)
            sub = plane[::4, ::4]
            frame_med.append(float(np.median(sub)))
            frame_mean.append(float(plane.mean()))
            if len(uniq) < 4096:
                uniq.update(np.unique(sub).tolist())
            is_dup = prev_plane is not None and np.array_equal(plane, prev_plane)
            dup_flags.append(bool(is_dup))
            dup_n += int(is_dup)
            prev_plane = plane
    out["packets"] = n
    out.update(decode_errors=sum(1 for e in errs if e["kind"] in ("zlib", "frame", "framing")),
               truncated_tail=any(e["kind"] == "truncated_tail" for e in errs),
               decode_error_list=errs[:max_gaps])
    if n == 0:
        return out

    infoN = np.array(infoN)
    seqs_a = np.asarray(seqs, dtype=np.int64)
    mono_a = np.asarray(mono, dtype=np.int64)
    mono_span = (mono_a[-1] - mono_a[0]) / 1e9 if n > 1 else 0.0
    have_recv = recv[0] is not None
    if have_recv:
        recv_a = np.asarray(recv, dtype=np.int64)
        recv_span = (recv_a[-1] - recv_a[0]) / 1e9 if n > 1 else 0.0
        t_s = (recv_a - recv_a[0]) / 1e9
        d_ms = np.diff(recv_a) / 1e6 if n > 1 else np.zeros(0)
        out.update(host_first_s=recv_a[0] / 1e9, host_last_s=recv_a[-1] / 1e9,
                   recv_span_s=round(recv_span, 4),
                   # time.time_ns() is a wall clock: a step (ntp, a manual set) would shift the
                   # alignment to the runner's launch times, so say when it is not monotone.
                   n_recv_backwards=int(np.sum(np.diff(recv_a) < 0)) if n > 1 else 0,
                   fps_recv=_fps(n, recv_span),
                   fps_seq=round(float(seqs_a[-1] - seqs_a[0]) / recv_span, 4) if recv_span > 0 else None,
                   recv_dt_ms_median=round(float(np.median(d_ms)), 3) if n > 1 else None,
                   recv_dt_ms_min=round(float(d_ms.min()), 3) if n > 1 else None,
                   recv_dt_ms_max=round(float(d_ms.max()), 3) if n > 1 else None,
                   recv_dt_ms_p99=round(float(np.percentile(d_ms, 99)), 3) if n > 1 else None,
                   recv_gaps_over_1s=[{"index": int(i + 1), "t_s": round(float(t_s[i]), 4),
                                       "dt_s": round(float(d_ms[i] / 1000.0), 4)}
                                      for i in np.nonzero(d_ms > 1000.0)[0][:max_gaps]])
    else:
        t_s = (mono_a - mono_a[0]) / 1e9
        out.update(host_first_s=None, host_last_s=None, recv_span_s=None, fps_recv=None,
                   fps_seq=round(float(seqs_a[-1] - seqs_a[0]) / mono_span, 4) if mono_span > 0 else None)
    d_mono = np.diff(mono_a) / 1e6 if n > 1 else np.zeros(0)
    out.update(mono_span_s=round(mono_span, 4), fps_mono=_fps(n, mono_span),
               mono_dt_ms_median=round(float(np.median(d_mono)), 3) if n > 1 else None,
               mono_dt_ms_min=round(float(d_mono.min()), 3) if n > 1 else None,
               mono_dt_ms_max=round(float(d_mono.max()), 3) if n > 1 else None,
               wall_first_ms=int(wall[0] // 1_000_000), wall_last_ms=int(wall[-1] // 1_000_000))
    out.update(_seq_report(seqs_a, t_s, max_list=max_gaps))
    fc = np.asarray(framecount, dtype=np.int64)
    # The InfoLine frame counter is the sensor's own 25 Hz tick, 16 bits, so differences wrap.
    # A step of 0 means the phone served the same sensor frame twice - which is what the shutter
    # does. A step above 1 means a sensor frame never reached the phone.
    fcd = (np.diff(fc) % 65536) if n > 1 else np.zeros(0, dtype=np.int64)
    out.update(magic=hdr0["magic"], ver=hdr0["ver"], w=hdr0["w"], h=hdr0["h"],
               gain_values=sorted(gain), auto_ffc=int(hdr0["auto_ffc"]), auto_ffc_values=sorted(auto_ffc),
               ffc_countdown_values=sorted(ffc_cd)[:16],
               fpa_c_first=round(fpa[0], 3), fpa_c_last=round(fpa[-1], 3),
               fpa_c_min=round(min(fpa), 3), fpa_c_max=round(max(fpa), 3),
               fpa_c_range=round(max(fpa) - min(fpa), 3),
               fpa_c_distinct=len(set(round(v, 4) for v in fpa)),
               framecount_contiguous=bool(np.all(fcd == 1)) if n > 1 else None,
               framecount_stalls=int(np.sum(fcd == 0)), framecount_skips=int(np.sum(fcd > 1)),
               framecount_missed=int(np.sum(fcd[fcd > 1] - 1)),
               framecount_first=int(fc[0]), framecount_last=int(fc[-1]),
               # A run of stalls is the shutter, and this one is visible in the header-only pass:
               # on a 5-minute idle capture these runs matched the frozen planes frame for frame.
               # Indexed like dup_runs: the first frame of the stalled group, counting every frame
               # in it (a run of `ln` equal steps covers `ln + 1` frames).
               framecount_stall_runs=[{"index": int(i0), "t_s": round(float(t_s[i0]), 4),
                                       "seq": int(seqs_a[i0]), "frames": int(ln + 1),
                                       "repeats": int(ln),
                                       "seconds": round(float(t_s[min(n - 1, i0 + ln)] - t_s[i0]), 4)}
                                      for i0, ln in _runs(fcd == 0)][:max_gaps],
               # The framing costs 12 B a frame in a .p3rec and 4 B in a /stream.raw.z capture;
               # take it off so this is the compressed frame, not the record.
               mean_compressed_frame_bytes=round(
                   (out["bytes"] - n * {"p3rec": _REC.size, "z": _LEN.size}.get(kind, 0)) / n, 1)
               if out["bytes"] else None,
               bytes_per_s=round(out["bytes"] / (out.get("recv_span_s") or mono_span), 1)
               if out["bytes"] and (out.get("recv_span_s") or mono_span) else None,
               infoline_first=info_temps(info0), infoline_last=info_temps(infoN))
    if frame_med:
        med_mk = np.asarray(frame_med) * MK_PER_LSB
        mean_mk = np.asarray(frame_mean) * MK_PER_LSB
        mean_c = np.asarray(frame_mean) / TEMP_SCALE - KELVIN_OFFSET
        dup_a = np.asarray(dup_flags, dtype=bool)
        lvl = mean_mk if step_stat == "mean" else med_mk
        d = np.diff(lvl) if n > 1 else np.zeros(0)
        d_mean = np.diff(mean_mk) if n > 1 else np.zeros(0)
        d_med = np.diff(med_mk) if n > 1 else np.zeros(0)
        jumps = []
        for i in np.nonzero(np.abs(d) > step_mk)[0][:max_gaps]:
            lo, hi = max(0, i - 12), min(n, i + 14)       # about +-0.5 s at 25 fps
            jumps.append({"index": int(i + 1), "t_s": round(float(t_s[i + 1]), 4),
                          "seq": int(seqs_a[i + 1]), "step_mk": round(float(d[i]), 2),
                          "seq_jump": int(seqs_a[i + 1] - seqs_a[i]),
                          "mk_before": round(float(lvl[i]), 2), "mk_after": round(float(lvl[i + 1]), 2),
                          "mean_step_mk": round(float(d_mean[i]), 2),
                          "median_step_mk": round(float(d_med[i]), 2),
                          "dup_frames_within_0p5s": int(dup_a[lo:hi].sum()),
                          "fpa_c": round(float(fpa[i + 1]), 3)})
        out.update(raw_min=raw_min, raw_max=raw_max, raw_step=_raw_step(np.asarray(sorted(uniq))),
                   raw_distinct_subsampled=len(uniq),
                   plane_min_c=round(raw_min / TEMP_SCALE - KELVIN_OFFSET, 4),
                   plane_max_c=round(raw_max / TEMP_SCALE - KELVIN_OFFSET, 4),
                   frame_mean_c_first=round(float(mean_c[0]), 4),
                   frame_mean_c_last=round(float(mean_c[-1]), 4),
                   frame_mean_c_ptp=round(float(np.ptp(mean_c)), 4),
                   mean_mk_ptp=round(float(np.ptp(mean_mk)), 2),
                   median_mk_ptp=round(float(np.ptp(med_mk)), 2),
                   max_abs_mean_step_mk=round(float(np.max(np.abs(d_mean))), 2) if n > 1 else None,
                   max_abs_median_step_mk=round(float(np.max(np.abs(d_med))), 2) if n > 1 else None,
                   step_stat=step_stat, step_mk_threshold=step_mk,
                   n_level_steps=int(np.sum(np.abs(d) > step_mk)),
                   n_median_steps=int(np.sum(np.abs(d_med) > step_mk)),
                   level_steps=jumps, dup_frames=dup_n, longest_dup_run=_longest_run(dup_a),
                   dup_runs=[_dup_run(i0, ln, n, t_s, seqs_a, fc, lvl) for i0, ln in _runs(dup_a)])
        out["ffc_runs"] = [r for r in out["dup_runs"] if r["kind"] == "shutter"]
        out["n_ffc_runs"] = len(out["ffc_runs"])
    return out


def _dup_run(i0: int, ln: int, n: int, t_s, seqs_a, fc, lvl) -> dict:
    """One run of bit-identical planes: frames [i0-1 .. i0+ln-1], and whether it is the shutter.

    `dup_a[i]` marks frame i as identical to i-1, so a run of `ln` flags starting at i0 means
    `ln + 1` identical frames starting at i0-1 - the first of which still carries the pre-shutter
    picture. Through a real shutter `seq` keeps stepping by 1 while the sensor's InfoLine framecount
    stalls; a frame the *recording* holds twice repeats `seq` too (a reconnect inside one frame
    time, or two recorders on one file), which is not a camera event at all.
    """
    a, b = max(0, i0 - 1), min(n - 1, i0 + ln - 1)
    seq_adv = int(seqs_a[b] - seqs_a[a])
    fc_adv = int((fc[b] - fc[a]) % 65536)
    return {"index": a, "t_s": round(float(t_s[a]), 4), "seq": int(seqs_a[a]),
            "frames": int(b - a + 1), "repeats": int(ln),
            "seconds": round(float(t_s[b] - t_s[a]), 4),
            "seq_advance": seq_adv, "framecount_advance": fc_adv,
            "kind": ("shutter" if seq_adv == b - a and fc_adv == 0
                     else "duplicate_records" if seq_adv == 0 else "unclear"),
            "level_step_mk": round(float(lvl[min(n - 1, b + 1)] - lvl[a]), 2)}


def _runs(flags):
    """[(start_index, length)] for every run of True in `flags`."""
    out, i, n = [], 0, len(flags)
    while i < n:
        if flags[i]:
            j = i
            while j < n and flags[j]:
                j += 1
            out.append((i, j - i))
            i = j
        else:
            i += 1
    return out


# ------------------------------------------------------------------------------------------- CLI

def _print(obj, quiet=False):
    if not quiet:
        print(json.dumps(obj, indent=1, default=_jsonable))


def _jsonable(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.bool_,)):
        return bool(o)
    raise TypeError(repr(o))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="p3rec.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")

    s = sub.add_parser("summarize", help="packets, fps, seq gaps, fpa_c, plane range, FFC candidates")
    s.add_argument("path")
    s.add_argument("--kind", choices=["auto", "z", "p3rec", "raw"], default="auto")
    s.add_argument("--fast", action="store_true", help="headers only: no planes, no degrees")
    s.add_argument("--step-mk", type=float, default=20.0,
                   help="flag frame-to-frame jumps in the whole-frame level above this (mK)")
    s.add_argument("--step-stat", choices=["mean", "median"], default="mean",
                   help="the level the jumps are flagged on; the median dithers by 62.5 mK (default: mean)")
    s.add_argument("--max-gaps", type=int, default=50, help="list at most this many gaps / steps")
    s.add_argument("--json", help="also write the summary here")
    s.add_argument("--npy", help="also save the uint16 cube (short captures only)")
    s.add_argument("--brief", action="store_true", help="a one-screen table instead of the JSON")
    s.add_argument("--quiet", action="store_true")

    e = sub.add_parser("ffc", help="the shutter events: frozen-plane runs and their per-pixel step")
    e.add_argument("path")
    e.add_argument("--kind", choices=["auto", "z", "p3rec", "raw"], default="auto")
    e.add_argument("--window", type=int, default=25,
                   help="frames averaged either side of a freeze to measure its step")
    e.add_argument("--min-run", type=int, default=2, help="shortest frozen run that counts")
    e.add_argument("--json", help="write the events here")
    e.add_argument("--quiet", action="store_true")

    j = sub.add_parser("steps", help="the whole-frame level track and its jumps (FFC / shutter candidates)")
    j.add_argument("path")
    j.add_argument("--kind", choices=["auto", "z", "p3rec", "raw"], default="auto")
    j.add_argument("--step-mk", type=float, default=20.0)
    j.add_argument("--stat", choices=["mean", "median"], default="mean")
    j.add_argument("--sub-px", type=int, default=4)
    j.add_argument("--json", help="write the jumps and both level tracks here")
    j.add_argument("--quiet", action="store_true")

    a = ap.parse_args(argv)
    if a.cmd is None:
        ap.print_help()
        return 2
    try:
        return _run(a)
    except (ValueError, EOFError, OSError, zlib.error) as e:
        # A file that is not a capture, or one whose framing is broken past the point the
        # non-strict iterators tolerate. One line, not a traceback.
        print("%s: %s: %s" % (a.path, type(e).__name__, e), file=sys.stderr)
        return 1


def _run(a) -> int:
    if a.cmd == "summarize":
        out = summarize(a.path, a.kind, fast=a.fast, step_mk=a.step_mk, max_gaps=a.max_gaps,
                        step_stat=a.step_stat)
        if a.brief:
            if not a.quiet:
                print(brief(out))
        else:
            _print(out, a.quiet)
        if a.json:
            with open(a.json, "w") as f:
                json.dump(out, f, indent=1, default=_jsonable)
        if a.npy:
            cube, _h, infos = load_cube(a.path, a.kind)
            np.save(a.npy, cube)
            base = a.npy[:-4] if a.npy.endswith(".npy") else a.npy
            np.save(base + "_info.npy", np.stack(infos) if infos else np.zeros((0, INFO_WORDS)))
            print("saved %s %s -> %s" % (cube.shape, cube.dtype, a.npy), file=sys.stderr)
        return 0

    if a.cmd == "ffc":
        evs = ffc_events(a.path, a.kind, window=a.window, min_run=a.min_run)
        if not a.quiet:
            print("%d frozen-plane events, %d of them the shutter"
                  % (len(evs), sum(1 for e in evs if e["kind"] == "shutter")))
            for ev in evs:
                print("  t=%9.3f s seq=%s %s  frozen %2d frames (%.2f s)  per-pixel step: "
                      "median %s  p5 %s  p95 %s  spread %s mK  [%d pre / %d post]%s"
                      % (ev["t_s"], ev["seq"], ev["kind"], ev["frames"], ev["seconds"],
                         json.dumps(ev["step_mk_median"]), json.dumps(ev["step_mk_p5"]),
                         json.dumps(ev["step_mk_p95"]), json.dumps(ev["step_mk_ptp"]),
                         ev["n_pre"], ev["n_post"],
                         "  since previous %.3f s" % ev["since_previous_s"]
                         if "since_previous_s" in ev else ""))
        if a.json:
            with open(a.json, "w") as f:
                json.dump(evs, f, indent=1, default=_jsonable)
        return 0

    if a.cmd == "steps":
        tr = level_track(a.path, a.kind, step_mk=a.step_mk, stat=a.stat, sub_px=a.sub_px)
        head = {k: tr[k] for k in ("n", "stat", "step_mk_threshold", "sub_px", "n_dup_frames",
                                   "longest_dup_run", "mean_mk_ptp", "median_mk_ptp",
                                   "max_abs_mean_step_mk", "max_abs_median_step_mk", "jumps")}
        _print(head, a.quiet)
        if a.json:
            with open(a.json, "w") as f:
                json.dump({**head,
                           "t_s": [round(float(v), 4) for v in tr["t_s"]],
                           "seq": tr["seq"].tolist(),
                           "mean_mk": [round(float(v), 3) for v in tr["mean_mk"]],
                           "median_mk": [round(float(v), 3) for v in tr["median_mk"]],
                           "dup": tr["dup"].tolist()}, f, default=_jsonable)
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
