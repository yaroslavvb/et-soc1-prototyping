#!/usr/bin/env python3
"""reduce_hm.py - E62 heat movies: one RUNDIR of raw thermal packets -> RED, the reduced cube.

    python3 reduce_hm.py <RUNDIR> --out <RED> [--cam <file>] [--kind auto|p3rec|z]
            [--t0 <epoch_s> --t1 <epoch_s>] [--bin-s 0.5] [--bin 2]
            [--ffc-thresh-mk 40] [--scene-s 60] [--max-frames N]

Standard library + numpy only, so it runs on the lab host (python 3.12, numpy 1.26) as well as
on the laptop.  Nothing here opens the card, the camera or the network: it only reads files.

What it does, in order
----------------------
1. Decodes the capture.  `p3rec.py` beside this file is used when it exports `iter_p3rec` /
   `parse_packet`; otherwise the minimal parser below reads the two wire formats of INTERFACES.md:
       .p3rec        repeat { uint64 LE host_recv_ns ; uint32 LE len ; len bytes of zlib blob }
       /stream.raw.z repeat { uint32 LE compressed_len ; zlib blob }            (no host stamps)
   A blob inflates to a 99,392-byte packet = 64 B header (magic P3FZ) + 1,024 B InfoLine
   + 192x256 uint16 LE plane in 1/64 K.  15.625 mK per count; the live preset quantises to
   multiples of 4 counts.
2. Finds the shutter (FFC) events *from the data*: a step in the whole-frame mean or in the global
   median, a sequence-number gap of a few frames, or a frozen (bit-identical) plane.  All of these
   are what an FFC looks like downstream; a gap or a freeze alone is not trusted.
3. Bridges each event per pixel: offset = median of ~0.5 s after minus median of ~0.5 s before,
   minus the local drift (a per-pixel linear fit on the +-(0.5..3.5) s shoulders).  Every later
   frame has the running sum of offsets subtracted, so the whole session sits on the first
   segment's offset map.
4. 2x2 bins to 96x128 and averages into 0.5 s bins on the *host* clock (the clock the runner's
   launch times use), so alignment needs no cross-machine offset.

Outputs (RED), exactly as INTERFACES.md specifies
-------------------------------------------------
    frames.npz   t_s float64[N] (bin centres, s since session t_start_ms), mk float32[N,96,128]
                 (absolute mK after bridging), n int16[N], ffc bool[N]
    scene.npy    float32[192,256] degC, full-resolution mean of the first idle minute
    ffc.json     [{t_s, seq, step_mk_median, step_mk_p95, method}]
    meta.json    bins, binning, fps, packets, dropped by seq, reconnect gaps, first/last frame
                 times, decode errors (and the knobs this run used)
    plus copies of session.json, launches.jsonl, phases.jsonl, blocks.jsonl, tel.jsonl, marks.jsonl
"""
from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import struct
import sys
import time
import zlib

import numpy as np

# ---------------------------------------------------------------- wire format

W, H = 256, 192
HDR_SIZE = 64
INFO_WORDS = 512                                   # 1,024 B InfoLine
PLANE_BYTES = W * H * 2                            # 98,304
SCI_SIZE = HDR_SIZE + 2 * INFO_WORDS + PLANE_BYTES  # 99,392
HDR_FMT = "<4sIqqqqqihhfBBH"
assert struct.calcsize(HDR_FMT) == HDR_SIZE
TEMP_SCALE = 64.0
KELVIN_OFFSET = 273.15
MK_PER_LSB = 1000.0 / TEMP_SCALE                   # 15.625 mK per count
_REC = struct.Struct("<QI")
DECODER = "built-in"          # set by iter_frames: the camera reader's p3rec.py when it is there


def parse_header(buf: bytes) -> dict:
    h = struct.unpack(HDR_FMT, buf[:HDR_SIZE])
    return dict(magic=h[0].decode("latin1"), ver=h[1], seq=h[2], mono_ns=h[3], wall_ns=h[4],
                cnt1=h[5], cnt2=h[6], cnt3=h[7], w=h[8], h=h[9], fpa_c=h[10],
                gain=h[11], auto_ffc=h[12])


def parse_packet(sci: bytes):
    """A decompressed 99,392-byte packet -> (hdr, InfoLine uint16[512], plane uint16[192,256])."""
    if len(sci) != SCI_SIZE:
        raise ValueError("expected %d packet bytes, got %d" % (SCI_SIZE, len(sci)))
    hdr = parse_header(sci)
    info = np.frombuffer(sci, dtype="<u2", count=INFO_WORDS, offset=HDR_SIZE)
    plane = np.frombuffer(sci, dtype="<u2", count=W * H,
                          offset=HDR_SIZE + 2 * INFO_WORDS).reshape(H, W)
    return hdr, info, plane


def _try_p3rec_module():
    """The camera reader's decoder library, when it is beside this file and speaks the API."""
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    try:
        import p3rec  # type: ignore
    except Exception:
        return None
    if all(hasattr(p3rec, n) for n in ("iter_p3rec", "parse_packet")):
        return p3rec
    return None


def iter_frames(path: str, kind: str = "auto", max_frames: int | None = None):
    """Yield (host_s or None, hdr, info, plane) for every frame of a capture.

    kind: 'p3rec' (host-stamped recording) or 'z' (a bare /stream.raw.z capture); 'auto' by suffix
    and by sniffing the first 4 bytes.
    """
    if kind == "auto":
        kind = "p3rec" if path.endswith(".p3rec") else None
        if kind is None:
            with open(path, "rb") as f:
                head = f.read(12)
            # In a .p3rec the first 8 bytes are a host epoch in ns (~1.8e18); in /stream.raw.z the
            # first 4 bytes are a compressed length (< 1e6).
            kind = "z"
            if len(head) >= 12:
                (lo,) = struct.unpack_from("<Q", head, 0)
                (clen,) = struct.unpack_from("<I", head, 0)
                if lo > 10 ** 17 and not 0 < clen < 10 ** 6:
                    kind = "p3rec"
    mod = _try_p3rec_module()
    global DECODER
    DECODER = "p3rec.py" if (mod is not None and kind == "p3rec") else "built-in"
    if mod is not None and kind == "p3rec":
        for i, rec in enumerate(mod.iter_p3rec(path)):
            recv_ns, hdr, info, plane = rec
            yield recv_ns / 1e9, hdr, info, plane
            if max_frames and i + 1 >= max_frames:
                return
        return
    n = 0
    with open(path, "rb") as f:
        while True:
            if kind == "p3rec":
                hb = f.read(_REC.size)
                if len(hb) < _REC.size:
                    return
                recv_ns, clen = _REC.unpack(hb)
                host_s = recv_ns / 1e9
            else:
                hb = f.read(4)
                if len(hb) < 4:
                    return
                (clen,) = struct.unpack("<I", hb)
                host_s = None
            if not 0 < clen < 10 ** 7:
                raise ValueError("bad frame length %d at offset %d" % (clen, f.tell() - 4))
            blob = f.read(clen)
            if len(blob) < clen:
                return                                     # truncated tail: the normal end
            try:
                sci = zlib.decompress(blob)
                hdr, info, plane = parse_packet(sci)
            except Exception as e:                          # noqa: BLE001 - keep going, count it
                yield ("decode-error", repr(e))             # sentinel the caller counts
                n += 1
                if max_frames and n >= max_frames:
                    return
                continue
            yield host_s, hdr, info, plane
            n += 1
            if max_frames and n >= max_frames:
                return


# ---------------------------------------------------------------- small numerics (shared)

def bin_plane(plane, k: int = 2) -> np.ndarray:
    """k x k box-average of a [H,W] plane -> [H/k, W/k] float32 (k must divide both)."""
    a = np.asarray(plane, dtype=np.float32)
    h, w = a.shape
    return a.reshape(h // k, k, w // k, k).mean(axis=(1, 3))


def gblur(img, sigma: float) -> np.ndarray:
    """Separable Gaussian over the last two axes, reflecting edges, NaN-safe (NaNs ignored)."""
    a = np.asarray(img, dtype=np.float32)
    if sigma is None or sigma <= 0:
        return a.copy()
    r = max(1, int(round(3.0 * sigma)))
    x = np.arange(-r, r + 1, dtype=np.float32)
    k = np.exp(-0.5 * (x / float(sigma)) ** 2)
    k /= k.sum()
    bad = ~np.isfinite(a)
    v = np.where(bad, 0.0, a).astype(np.float32)
    wts = (~bad).astype(np.float32)
    for axis in (-2, -1):
        v = _conv1d_reflect(v, k, axis)
        wts = _conv1d_reflect(wts, k, axis)
    out = np.where(wts > 1e-6, v / np.maximum(wts, 1e-6), np.nan).astype(np.float32)
    return out


def _conv1d_reflect(a, k, axis):
    r = (len(k) - 1) // 2
    a = np.moveaxis(a, axis, -1)
    pad = [(0, 0)] * (a.ndim - 1) + [(r, r)]
    ap = np.pad(a, pad, mode="reflect")
    out = np.zeros_like(a)
    for i, kk in enumerate(k):
        out += kk * ap[..., i:i + a.shape[-1]]
    return np.moveaxis(out, -1, axis)


def median3(img, size: int = 3) -> np.ndarray:
    """size x size median filter over the last two axes (odd size), reflecting edges.

    Vectorised over any leading axes, so a whole batch of permutation maps goes through in one
    call; the finite fast path uses a partial sort instead of nanmedian, which is several times
    quicker and is what the permutation loop lives on.
    """
    a = np.asarray(img, dtype=np.float32)
    r = size // 2
    pad = [(0, 0)] * (a.ndim - 2) + [(r, r), (r, r)]
    ap = np.pad(a, pad, mode="reflect")
    hs, ws = a.shape[-2], a.shape[-1]
    stack = np.stack([ap[..., i:i + hs, j:j + ws] for i in range(size) for j in range(size)],
                     axis=0)
    k = stack.shape[0] // 2
    if np.isfinite(a).all():
        return np.partition(stack, k, axis=0)[k].astype(np.float32)
    return np.nanmedian(stack, axis=0).astype(np.float32)


def load_jsonl(path: str):
    out = []
    if not path or not os.path.exists(path):
        return out
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:                              # noqa: BLE001 - a half-written tail
                continue
    return out


# ---------------------------------------------------------------- FFC detection

def detect_ffc(t, seq, fmean, fmed, frozen, thresh_mk: float):
    """Candidate shutter events from the per-frame scalars.

    Returns a list of dicts {i_before, i_after, t_before, t_after, seq, step_raw_mk, cues}.
    i_before is the index of the last frame on the old offset map, i_after the first on the new.

    Cues, each of which an FFC really produces downstream:
      mean_step   - the whole-frame mean jumps by more than `thresh_mk`: the offset map changed.
                    Over 49,152 pixels the mean's own noise is 0.15 mK and the drift is 0.3 mK per
                    frame, so a 40 mK jump in 40 ms is not the board and not the noise.
      median_step - the global median jumps by two quantisation steps or more (the live preset
                    rounds to 4 counts = 62.5 mK, so the median is a coarse instrument; it is here
                    because a shutter that moves most of the frame moves the median too)
      seq_gap     - 1..40 sequence numbers missing: the ~350-500 ms mechanical actuation, which the
                    frame parser drops as a partial frame rather than passing on corrupt data
      frozen      - the plane repeated bit for bit (a stale frame served during the shutter)
    A step alone is enough to need bridging; a gap or a freeze alone is accepted only with a
    quarter-threshold step, so that a reconnect or a dropped packet is not mistaken for a shutter.
    """
    n = len(t)
    ev = []
    if n < 4:
        return ev
    d = np.diff(fmean)
    dmed = np.diff(fmed)
    dseq = np.diff(seq)
    dt = np.diff(t)
    # robust scale of the frame-to-frame step, so the threshold adapts to the capture
    mad = float(np.median(np.abs(d - np.median(d)))) * 1.4826
    hard = max(float(thresh_mk), 6.0 * mad)
    soft = hard / 4.0
    for i in range(n - 1):
        cues = []
        gap_frames = int(dseq[i]) - 1
        if 1 <= gap_frames <= 40 and dt[i] < 2.0:
            cues.append("seq_gap")
        if frozen[i + 1] or frozen[i]:
            cues.append("frozen")
        step = float(d[i])
        small = bool(cues) and abs(step) >= soft          # a gap or a freeze with a smaller step
        if abs(step) >= hard:
            cues.append("mean_step")
        elif small:
            cues.append("small_step")
        if abs(float(dmed[i])) >= max(2.0 * 4.0 * MK_PER_LSB, 2.0 * hard):
            cues.append("median_step")
        if "mean_step" in cues or "median_step" in cues or small:
            ev.append(dict(i_before=i, i_after=i + 1, t_before=float(t[i]),
                           t_after=float(t[i + 1]), seq=int(seq[i + 1]),
                           step_raw_mk=step, gap_frames=gap_frames, cues=sorted(set(cues))))
    # merge events closer together than 1 s (one shutter can show as a gap *and* a step a frame later)
    merged = []
    for e in ev:
        if merged and e["t_before"] - merged[-1]["t_after"] < 1.0:
            m = merged[-1]
            m["i_after"] = e["i_after"]
            m["t_after"] = e["t_after"]
            m["step_raw_mk"] += e["step_raw_mk"]
            m["gap_frames"] += e["gap_frames"]
            m["cues"] = sorted(set(m["cues"]) | set(e["cues"]))
        else:
            merged.append(dict(e))
    return merged


# ---------------------------------------------------------------- the reduction

def reduce_run(rundir, out, cam=None, kind="auto", t0=None, t1=None, bin_s=0.5, binning=2,
               ffc_thresh_mk=40.0, scene_s=60.0, max_frames=None, no_ffc=False,
               no_shrink=False, verbose=True):
    t_wall = time.time()
    os.makedirs(out, exist_ok=True)
    rundir = os.path.abspath(rundir) if rundir else None

    # ---- the session's files
    session = {}
    if rundir and os.path.exists(os.path.join(rundir, "session.json")):
        with open(os.path.join(rundir, "session.json")) as f:
            session = json.load(f)
    cam_path = cam
    if cam_path is None and rundir:
        for cand in ("cam/cam.p3rec", "cam/cam.p3z", "cam/stream.raw.z"):
            if os.path.exists(os.path.join(rundir, cand)):
                cam_path = os.path.join(rundir, cand)
                break
    if cam_path is None or not os.path.exists(cam_path):
        raise SystemExit("no camera capture found (looked for cam/cam.p3rec under the RUNDIR)")

    # host-clock anchors for a capture with no per-frame host stamps
    done = {}
    camdir = os.path.dirname(cam_path)
    if os.path.exists(os.path.join(camdir, "done.json")):
        with open(os.path.join(camdir, "done.json")) as f:
            done = json.load(f)
    def _sidecar(name):
        p = os.path.join(camdir, name)
        if not os.path.exists(p):
            return None
        with open(p) as f:
            txt = f.read().strip()
        try:
            return float(txt)
        except ValueError:
            return None
    if t0 is None:
        t0 = _sidecar("cam.t0")
    if t1 is None:
        t1 = _sidecar("cam.t1")
    if t0 is None:
        t0 = done.get("first_host_s", done.get("t_first_s"))
    if t1 is None:
        t1 = done.get("last_host_s", done.get("t_last_s"))

    # ---- pass 1: per-frame scalars, FFC detection
    hosts, seqs, monos, fmean, fmed, frozen, fpa = [], [], [], [], [], [], []
    decode_errors = []
    prev_bytes = None
    for rec in iter_frames(cam_path, kind, max_frames):
        if isinstance(rec, tuple) and len(rec) == 2 and rec[0] == "decode-error":
            decode_errors.append(rec[1])
            continue
        host_s, hdr, info, plane = rec
        b = plane.tobytes()
        frozen.append(prev_bytes is not None and b == prev_bytes)
        prev_bytes = b
        hosts.append(host_s if host_s is not None else np.nan)
        seqs.append(int(hdr["seq"]))
        monos.append(int(hdr["mono_ns"]))
        fpa.append(float(hdr["fpa_c"]))
        a = plane.astype(np.float32)
        fmean.append(float(a.mean()) * MK_PER_LSB)
        fmed.append(float(np.median(a)) * MK_PER_LSB)
    nfr = len(seqs)
    if nfr < 4:
        raise SystemExit("only %d frames decoded from %s" % (nfr, cam_path))
    seqs = np.asarray(seqs, dtype=np.int64)
    monos = np.asarray(monos, dtype=np.int64)
    fmean = np.asarray(fmean, dtype=np.float64)
    fmed = np.asarray(fmed, dtype=np.float64)
    frozen = np.asarray(frozen, dtype=bool)
    hosts = np.asarray(hosts, dtype=np.float64)

    # ---- the host clock
    # A .p3rec stamps every frame.  A bare /stream.raw.z does not, so the phone's own monotonic
    # clock is anchored on the capture's start (and stretched onto its end when both are known).
    mono_s = (monos - monos[0]) / 1e9
    host_src = "p3rec"
    if not np.all(np.isfinite(hosts)):
        if t0 is None:
            raise SystemExit("this capture carries no host times: pass --t0 (and --t1)")
        if t1 is not None and mono_s[-1] > 0:
            span = float(t1) - float(t0)
            scale = span / mono_s[-1] if mono_s[-1] > 0 else 1.0
            if not 0.5 < scale < 2.0:
                scale = 1.0
            hosts = float(t0) + mono_s * scale
            host_src = "mono-anchored-t0-t1"
        else:
            hosts = float(t0) + mono_s
            host_src = "mono-anchored-t0"
    t_start_ms = session.get("t_start_ms")
    if t_start_ms is None:
        t_start_ms = float(t0) * 1000.0 if t0 is not None else float(hosts[0]) * 1000.0
    t_zero = float(t_start_ms) / 1000.0
    t = hosts - t_zero                                       # seconds since the session's start

    # ---- FFC events
    events = [] if no_ffc else detect_ffc(t, seqs, fmean, fmed, frozen, ffc_thresh_mk)
    seg_of = np.zeros(nfr, dtype=np.int32)
    for k, e in enumerate(events):
        seg_of[e["i_after"]:] = k + 1
    nseg = len(events) + 1

    # ---- windows each event needs (clipped to its own segment, >= 3 frames each)
    def win(lo_t, hi_t, lo_i, hi_i):
        idx = np.nonzero((t >= lo_t) & (t <= hi_t) & (~frozen))[0]
        return idx[(idx >= lo_i) & (idx <= hi_i)]

    half = max(0.5, bin_s)
    for k, e in enumerate(events):
        ib, ia = e["i_before"], e["i_after"]
        lo_i = events[k - 1]["i_after"] if k > 0 else 0
        hi_i = events[k + 1]["i_before"] if k + 1 < len(events) else nfr - 1
        wb = win(t[ib] - half, t[ib] + 1e-9, lo_i, ib)
        wa = win(t[ia] - 1e-9, t[ia] + half, ia, hi_i)
        grow = half
        while len(wb) < 3 and grow < 3.0:
            grow *= 2
            wb = win(t[ib] - grow, t[ib] + 1e-9, lo_i, ib)
        grow = half
        while len(wa) < 3 and grow < 3.0:
            grow *= 2
            wa = win(t[ia] - 1e-9, t[ia] + grow, ia, hi_i)
        e["w_before"] = wb
        e["w_after"] = wa
        e["d_before"] = win(t[ib] - 3.5, t[ib] - half, lo_i, ib)
        e["d_after"] = win(t[ia] + half, t[ia] + 3.5, ia, hi_i)

    # ---- the bin grid on the host clock
    good = ~frozen
    bi = np.floor(t / bin_s).astype(np.int64)
    b_lo, b_hi = int(bi[good].min()), int(bi[good].max())
    nb = b_hi - b_lo + 1
    hb, wb_ = H // binning, W // binning
    acc = np.zeros((nb, hb, wb_), dtype=np.float64)
    cnt = np.zeros(nb, dtype=np.int64)
    seg_cnt = np.zeros((nb, nseg), dtype=np.int64)
    ffc_in_bin = np.zeros(nb, dtype=bool)
    for e in events:
        for i_e in (e["i_before"], e["i_after"]):
            k = int(np.floor(t[i_e] / bin_s)) - b_lo
            if 0 <= k < nb:
                ffc_in_bin[k] = True

    # per-event accumulators
    for e in events:
        e["Bstack"], e["Astack"] = [], []
        e["dacc"] = {s: dict(n=0, st=0.0, stt=0.0, sb=np.zeros((hb, wb_), np.float64),
                             stb=np.zeros((hb, wb_), np.float64)) for s in ("pre", "post")}
    ev_before = {i: k for k, e in enumerate(events) for i in e["w_before"]}
    ev_after = {i: k for k, e in enumerate(events) for i in e["w_after"]}
    ev_dpre = {i: k for k, e in enumerate(events) for i in e["d_before"]}
    ev_dpost = {i: k for k, e in enumerate(events) for i in e["d_after"]}

    # ---- the scene window: the first idle minute (full resolution)
    scene_lo, scene_hi, scene_why = _scene_window(rundir, session, t, scene_s, events)
    scene_sum = np.zeros((H, W), dtype=np.float64)
    scene_n = 0

    # ---- pass 2: planes
    i = -1
    for rec in iter_frames(cam_path, kind, max_frames):
        if isinstance(rec, tuple) and len(rec) == 2 and rec[0] == "decode-error":
            continue
        i += 1
        host_s, hdr, info, plane = rec
        if frozen[i]:
            continue
        b = bin_plane(plane, binning) * MK_PER_LSB
        k = int(bi[i]) - b_lo
        acc[k] += b
        cnt[k] += 1
        seg_cnt[k, seg_of[i]] += 1
        if i in ev_before:
            events[ev_before[i]]["Bstack"].append(b)
        if i in ev_after:
            events[ev_after[i]]["Astack"].append(b)
        for tag, table in (("pre", ev_dpre), ("post", ev_dpost)):
            if i in table:
                d = events[table[i]]["dacc"][tag]
                ti = float(t[i])
                d["n"] += 1
                d["st"] += ti
                d["stt"] += ti * ti
                d["sb"] += b
                d["stb"] += ti * b
        if scene_lo <= t[i] <= scene_hi:
            scene_sum += plane.astype(np.float64)
            scene_n += 1

    # ---- per-event per-pixel offsets
    ffc_json = []
    offs = np.zeros((nseg, hb, wb_), dtype=np.float32)       # cumulative, per segment
    for k, e in enumerate(events):
        bst = np.stack(e["Bstack"]) if e["Bstack"] else None
        ast = np.stack(e["Astack"]) if e["Astack"] else None
        mb = np.median(bst, axis=0) if bst is not None else None
        ma = np.median(ast, axis=0) if ast is not None else None
        shrink = None
        if mb is None or ma is None:
            step = np.full((hb, wb_), e["step_raw_mk"], dtype=np.float32)
            method = "+".join(e["cues"]) + "+scalar-fallback"
        else:
            tb = float(np.mean(t[e["w_before"]]))
            ta = float(np.mean(t[e["w_after"]]))
            slope = _drift_slope(e["dacc"], hb, wb_)
            step = (ma - mb) - slope * (ta - tb)
            method = "+".join(e["cues"]) + ("+drift" if slope is not None else "")
            if slope is None:
                step = ma - mb
            shoulder = _shoulder_step(e["dacc"], slope)
            if shoulder is not None:
                e["shoulder_mk"] = round(float(np.median(shoulder)), 2)
            if not no_shrink:
                step, shrink = _shrink_step(step, shoulder, bst, ast)
                method += "+shrink%.2f" % shrink["k"]
        offs[k + 1:] += step.astype(np.float32)
        ffc_json.append(dict(t_s=round(float(t[e["i_after"]]), 3), seq=int(e["seq"]),
                             step_mk_median=round(float(np.median(step)), 2),
                             step_mk_p95=round(float(np.percentile(step, 95)), 2),
                             method=method, gap_frames=int(e["gap_frames"]),
                             frames_before=int(len(e["w_before"])),
                             frames_after=int(len(e["w_after"])),
                             step_mk_shoulders=e.get("shoulder_mk"),
                             shrink=shrink,
                             frame_mean_step_mk=round(float(e["step_raw_mk"]), 2)))

    # ---- bridge, divide, fill
    # A bin that straddles a shutter holds frames from both sides, so the correction is the
    # frame-weighted sum of the segments' running offsets - exact, and done bin by bin so a
    # 75-minute session does not need a second full cube in memory.
    mk = np.full((nb, hb, wb_), np.nan, dtype=np.float32)
    nz = cnt > 0
    for j in np.nonzero(nz)[0]:
        v = acc[j]
        for sgi in np.nonzero(seg_cnt[j])[0]:
            if sgi:
                v = v - float(seg_cnt[j, sgi]) * offs[sgi]
        mk[j] = (v / cnt[j]).astype(np.float32)
    t_s = (np.arange(b_lo, b_hi + 1, dtype=np.float64) + 0.5) * bin_s
    filled = int((~nz).sum())
    if filled and nz.sum() >= 2:                             # linear fill so consumers see no NaN
        idx = np.nonzero(nz)[0]
        for j in np.nonzero(~nz)[0]:
            lo = idx[idx < j]
            hi = idx[idx > j]
            if len(lo) and len(hi):
                a, b2 = lo[-1], hi[0]
                w = (j - a) / float(b2 - a)
                mk[j] = (1 - w) * mk[a] + w * mk[b2]
            elif len(lo):
                mk[j] = mk[lo[-1]]
            else:
                mk[j] = mk[hi[0]]

    # ---- scene
    if scene_n:
        scene = (scene_sum / scene_n) / TEMP_SCALE - KELVIN_OFFSET
    else:
        scene = np.full((H, W), np.nan)
        scene_why += "; no frames in the window"
    np.save(os.path.join(out, "scene.npy"), scene.astype(np.float32))

    # ---- meta
    dseq = np.diff(seqs)
    ffc_times = [float(t[e["i_after"]]) for e in events]
    gaps = [dict(t_s=round(float(t[i + 1]), 3), dt_s=round(float(t[i + 1] - t[i]), 3),
                 missing_seq=int(dseq[i] - 1))
            for i in np.nonzero((np.diff(t) > 1.0) | (dseq > 40))[0][:200]
            if not any(abs(float(t[i + 1]) - ft) < 1.5 for ft in ffc_times)]
    span = float(t[-1] - t[0])
    meta = dict(
        tool="reduce_hm.py", version=1,
        rundir=rundir, cam=os.path.abspath(cam_path), cam_bytes=os.path.getsize(cam_path),
        kind=kind, decoder=DECODER, host_clock=host_src, t_zero_epoch_s=t_zero,
        packets=int(nfr), decode_errors=len(decode_errors),
        decode_error_examples=decode_errors[:5],
        seq_first=int(seqs[0]), seq_last=int(seqs[-1]),
        dropped_by_seq=int((seqs[-1] - seqs[0] + 1) - nfr),
        frozen_frames=int(frozen.sum()),
        fps=round((nfr - 1) / span, 3) if span > 0 else None,
        first_frame_t_s=round(float(t[0]), 3), last_frame_t_s=round(float(t[-1]), 3),
        first_frame_epoch_s=float(hosts[0]), last_frame_epoch_s=float(hosts[-1]),
        reconnect_gaps=gaps, n_reconnect_gaps=len(gaps),
        bins=int(nb), bin_s=bin_s, binning=binning, shape=[int(hb), int(wb_)],
        empty_bins_filled=filled, fill_method="linear-in-time" if filled else None,
        bins_with_ffc=int(ffc_in_bin.sum()), ffc_events=len(events),
        ffc_thresh_mk=ffc_thresh_mk, ffc_disabled=bool(no_ffc),
        ffc_shrink=not bool(no_shrink),
        ffc_shrink_k_median=(round(float(np.median([e["shrink"]["k"] for e in ffc_json
                                                    if e.get("shrink")])), 4)
                             if any(e.get("shrink") for e in ffc_json) else None),
        mk_per_lsb=MK_PER_LSB, quantum_counts=_quantum(cam_path, kind, max_frames),
        scene_window_s=[round(scene_lo, 3), round(scene_hi, 3)], scene_frames=int(scene_n),
        scene_source=scene_why,
        fpa_c_first=round(float(fpa[0]), 3), fpa_c_last=round(float(fpa[-1]), 3),
        frame_mean_mk_first=round(float(fmean[0]), 1), frame_mean_mk_last=round(float(fmean[-1]), 1),
        frame_median_mk_ptp=round(float(np.ptp(fmed)), 1),
        elapsed_s=round(time.time() - t_wall, 2),
    )
    with open(os.path.join(out, "meta.json"), "w") as f:
        json.dump(meta, f, indent=1)
    with open(os.path.join(out, "ffc.json"), "w") as f:
        json.dump(ffc_json, f, indent=1)
    np.savez_compressed(os.path.join(out, "frames.npz"), t_s=t_s, mk=mk,
                        n=np.minimum(cnt, 32767).astype(np.int16), ffc=ffc_in_bin)

    # ---- the runner's own files, copied beside the cube
    if rundir:
        for nm in ("session.json", "launches.jsonl", "phases.jsonl", "blocks.jsonl",
                   "tel.jsonl", "marks.jsonl", "protocol.json"):
            src = os.path.join(rundir, nm)
            if os.path.exists(src):
                shutil.copyfile(src, os.path.join(out, nm))
    if verbose:
        print("RED %s: %d bins x %dx%d, %d packets, %.2f fps, %d FFC, scene %d frames (%.1f s)"
              % (out, nb, hb, wb_, nfr, meta["fps"] or 0, len(events), scene_n, meta["elapsed_s"]))
    return meta


def _shrink_step(step, shoulder, bst, ast):
    """Bridge only the part of a shutter step that is still there three seconds later.

    A step map is `median(after) - median(before)` over about half a second each way.  Its
    *common mode* - the spatial median - is pinned down to a fraction of a mK by 12,288 pixels,
    and on real frames it is small (median |step| 4.5 mK over the idle capture's 24 events).  Its
    *per-pixel* part is large, 14-156 mK, and it is mostly not an offset-map change at all: it is
    the camera's own post-shutter transient, the corners warming against the centre over the next
    ten or twenty seconds.  Subtracting a transient as if it were permanent makes every pixel's
    offset a random walk.  Measured on the idle capture: each pixel's own level spread 30 mK with
    no bridging against 113 mK with it, and the permutation null's SD came out 1.6-4.7x larger on
    three of four fake schedules.  That is the detection floor, paid for nothing.

    The discriminator is persistence, not size.  `step` is measured from the half-second either
    side; `shoulder` is the same step from the +-(0.5..3.5) s shoulders, a disjoint set of frames.
    A real offset-map change gives the same per-pixel map both ways; a fast transient has moved on
    and noise does not repeat, so the regression coefficient k = <devA, devB> / <devA, devA> is
    near 1 for the first and near 0 for the other two.  Because the two frame sets are disjoint
    their noises are independent, so k is biased *down* by noise - the conservative direction.
    The common mode is always kept in full: it is the part that is actually measured.

    Returns (step, {k, ...}).
    """
    med = float(np.median(step))
    dev = (step - med).astype(np.float64)
    daa = float((dev * dev).sum())
    v2 = 0.0
    for stck in (bst, ast):
        if stck is None or len(stck) < 2:
            continue
        # variance of a median of n: ~ pi/2 times the mean's, which is var/n
        v2 += 1.57 * float(np.mean(np.var(stck.astype(np.float64), axis=0, ddof=1))) / len(stck)
    info = dict(sigma_mk=round(float(math.sqrt(max(v2, 0.0))), 2),
                dev_mk=round(float(math.sqrt(daa / max(dev.size, 1))), 2),
                common_mk=round(med, 2))
    if shoulder is None or daa <= 0:
        # no shoulders to check against: fall back to the variance test, which catches noise but
        # not a transient, and say which test was used
        obs = daa / max(dev.size, 1)
        s2 = max(0.0, obs - v2)
        k = s2 / (s2 + v2) if (s2 + v2) > 0 else 1.0
        info.update(k=round(float(k), 4), test="variance (no shoulders)")
        return (med + k * dev).astype(np.float32), info
    devb = (np.asarray(shoulder, dtype=np.float64) - float(np.median(shoulder)))
    k = float((dev * devb).sum() / daa)
    k = min(1.0, max(0.0, k))
    info.update(k=round(k, 4), test="shoulder persistence",
                shoulder_dev_mk=round(float(np.sqrt((devb * devb).mean())), 2))
    return (med + k * dev).astype(np.float32), info


def _shoulder_step(dacc, slope):
    """The same step measured from the 0.5-3.5 s shoulders instead of the 0.5 s windows.

    A real shutter replaces the offset map, so the two agree; a single bad frame or a transient
    does not persist and the shoulder step comes back near zero.  Reported, never subtracted.
    """
    pre, post = dacc["pre"], dacc["post"]
    if pre["n"] < 3 or post["n"] < 3:
        return None
    mpre = pre["sb"] / pre["n"]
    mpost = post["sb"] / post["n"]
    dt = post["st"] / post["n"] - pre["st"] / pre["n"]
    out = mpost - mpre
    if slope is not None:
        out = out - slope * dt
    return out


def _drift_slope(dacc, hb, wb_):
    """Per-pixel mK/s from the +-(0.5..3.5) s shoulders; None when neither shoulder has 5 frames."""
    sl, got = np.zeros((hb, wb_), np.float64), 0
    for tag in ("pre", "post"):
        d = dacc[tag]
        n = d["n"]
        if n < 5:
            continue
        den = n * d["stt"] - d["st"] ** 2
        if abs(den) < 1e-9:
            continue
        sl += (n * d["stb"] - d["st"] * d["sb"]) / den
        got += 1
    return (sl / got).astype(np.float32) if got else None


def _scene_window(rundir, session, t, scene_s, events):
    """The session's first idle minute: the quiet time before the first launch when there is
    enough of it, else the first idle phase of 20 s or more, else just the capture's start."""
    lo = float(t[0])
    hi = lo + scene_s
    why = "capture start"
    if rundir:
        t_zero = float(session.get("t_start_ms", 0.0)) / 1000.0
        la = load_jsonl(os.path.join(rundir, "launches.jsonl"))
        starts = [l.get("t_start_ms") for l in la if l.get("t_start_ms")]
        first = (min(starts) / 1000.0 - t_zero) if starts else None
        if first is not None and first - float(t[0]) >= 10.0:
            lo, hi, why = float(t[0]), min(first, float(t[0]) + scene_s), "before the first launch"
        else:
            for p in [q for q in load_jsonl(os.path.join(rundir, "phases.jsonl")) if q.get("idle")]:
                a, b = p.get("planned_start_ms"), p.get("planned_end_ms")
                if a is None or b is None:
                    continue
                a, b = a / 1000.0 - t_zero, b / 1000.0 - t_zero
                if b - a >= min(20.0, scene_s) and b >= t[0] and a <= t[-1]:
                    lo, hi, why = max(a, float(t[0])), min(b, max(a, float(t[0])) + scene_s), \
                        "first idle phase"
                    break
    for e in events:                                         # never average across a shutter
        te = float(t[e["i_before"]])
        if lo < te < hi:
            hi = te
            why += " (cut at the first shutter)"
            break
    return lo, min(hi, float(t[-1])), why


def _quantum(cam_path, kind, max_frames):
    """The capture's real count step (4 under the live preset, 1 in raw), from the first frames."""
    vals = set()
    n = 0
    for rec in iter_frames(cam_path, kind, 20 if not max_frames else min(20, max_frames)):
        if isinstance(rec, tuple) and len(rec) == 2 and rec[0] == "decode-error":
            continue
        vals.update(np.unique(rec[3]).tolist())
        n += 1
        if n >= 20:
            break
    v = np.array(sorted(vals), dtype=np.int64)
    if len(v) < 3:
        return None
    d = np.diff(v)
    d = d[d > 0]
    if not len(d):
        return None
    g = int(d[0])
    for x in d:
        a, b = g, int(x)
        while b:
            a, b = b, a % b
        g = a
    return int(g)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("rundir", nargs="?", help="the RUNDIR written by the runner")
    ap.add_argument("--out", required=True)
    ap.add_argument("--cam", help="the capture, when it is not <RUNDIR>/cam/cam.p3rec")
    ap.add_argument("--kind", default="auto", choices=["auto", "p3rec", "z"])
    ap.add_argument("--t0", type=float, help="host epoch s of the capture's first frame (raw captures)")
    ap.add_argument("--t1", type=float, help="host epoch s of its last frame")
    ap.add_argument("--bin-s", type=float, default=0.5)
    ap.add_argument("--bin", type=int, default=2, dest="binning")
    ap.add_argument("--ffc-thresh-mk", type=float, default=40.0)
    ap.add_argument("--scene-s", type=float, default=60.0)
    ap.add_argument("--max-frames", type=int)
    ap.add_argument("--no-ffc", action="store_true", help="skip shutter detection entirely")
    ap.add_argument("--no-ffc-shrink", action="store_true", dest="no_shrink",
                    help="bridge each shutter step per pixel as measured, without shrinking the "
                         "part of it that is noise (the old behaviour)")
    ap.add_argument("-q", "--quiet", action="store_true")
    a = ap.parse_args(argv)
    reduce_run(a.rundir, a.out, cam=a.cam, kind=a.kind, t0=a.t0, t1=a.t1, bin_s=a.bin_s,
               binning=a.binning, ffc_thresh_mk=a.ffc_thresh_mk, scene_s=a.scene_s,
               max_frames=a.max_frames, no_ffc=a.no_ffc, no_shrink=a.no_shrink,
               verbose=not a.quiet)


if __name__ == "__main__":
    main()
