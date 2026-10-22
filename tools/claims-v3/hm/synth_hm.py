#!/usr/bin/env python3
"""synth_hm.py - a synthetic E62 RUNDIR with planted ground truth, in the real wire formats.

    python3 synth_hm.py --protocol <protocol.json> --out <RUNDIR> [--fps 5] [--seed 1] ...
    python3 synth_hm.py --write-demo-protocol <path>      # the small protocol the tests use

Why it exists: `reduce_hm.py` and `analyze_hm.py` must be shown to recover a *known* answer before
anyone believes them on card data.  So this writes a whole RUNDIR - `cam/cam.p3rec` byte for byte in
the recording format of INTERFACES.md, plus `launches.jsonl`, `phases.jsonl`, `blocks.jsonl`,
`tel.jsonl`, `session.json`, `marks.jsonl` - from a planted model of what the back of the board does:

  * a Gaussian blob per active shire, placed by an affine die->image map with a chosen roll and
    mirror (so the orientation fit has a right answer to find),
  * blur sigma of a centimetre or two in pixels (the copper's blur, not the lens's),
  * a chosen amplitude per watt, with a first-order lag of ~10-20 s (heat arrives late),
  * a whole-field drift of a few mK/s, plus the camera's own radial post-shutter drift,
  * shutter (FFC) steps every ~90 s: a frozen frame, a sequence gap, and a new per-pixel offset map,
  * per-pixel low-emissivity gain on the signal (the shiny component tops),
  * 34 mK of frame noise and the live preset's quantisation to multiples of 4 counts.

It also writes `<RUNDIR>/truth/truth.json` (every planted number, and the per-block expected die
displacement) and `<RUNDIR>/truth/red/` - a *clean* RED (no noise, no drift, no shutter, no
emissivity) on the identical bin grid.  Running `analyze_hm.py` on both and comparing is the test:
the same estimator, the same smoothing, the same projection, one with artefacts and one without.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import struct
import sys
import time
import zlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from reduce_hm import (H, HDR_FMT, INFO_WORDS, KELVIN_OFFSET, MK_PER_LSB,  # noqa: E402
                       W, bin_plane, gblur)

# The MARTY 6x6 die map: rows r0..r5 (r0 the I/O edge, the short N-S axis), columns c1..c6 (the long
# W-E axis).  None = a non-compute cell (master/spare, IO/PCIe).  Public: tools/claims-v3/hp.
DIE_GRID = [
    [0, 8, 3, None, None, None],
    [24, 16, 4, 12, 20, 28],
    [9, 1, 13, 21, 29, 5],
    [25, 17, 14, 22, 30, 6],
    [2, 10, 18, 26, 15, 7],
    [11, 19, 27, None, 23, 31],
]
SHIRE_RC = {s: (r, c) for r, row in enumerate(DIE_GRID) for c, s in enumerate(row) if s is not None}

MASKS = {  # verified against DIE_GRID by `--write-demo-protocol`
    "W12": 0x03076616, "E12": 0x747090E0, "N12": 0x31313232, "S12": 0x4646C4C4,
    "B4NW": 0x01010101, "B4NE": 0x30100020, "B4SW": 0x00080C04, "B4SE": 0x80808080,
    "B4C": 0x00606000, "CEN8": 0x04647010, "ALL32": 0xFFFFFFFF,
}


def shires_of(mask: int):
    return [s for s in range(32) if mask >> s & 1]


# ---------------------------------------------------------------- the demo protocol

def demo_protocol():
    """A small protocol: the bloom, N<->S, W<->E, a four-corner sequence, and a null pair.

    Short dwells, and `cycles` counted the runner's way (it runs warmup_cycles + cycles laps), so
    7 usable cycles against a sign-flip floor of 2/2^7 = 0.0156 - room to see p < 0.05, which 5
    usable cycles (floor 0.0625) would not have.  `we` alternates its arm order and `ns` does not,
    so one canonical run covers both, and with them the drift leak that only the as-given order
    admits.  The predictions and pass rules are sized for this file's own default plant: they are
    test thresholds, not the registered predictions of a card run.
    """
    def st(mask, per_shire=32):
        sh = shires_of(mask)
        rows = [SHIRE_RC[s][0] for s in sh]
        cols = [SHIRE_RC[s][1] for s in sh]
        return dict(shires=sh, mask="0x%08x" % mask, per_shire=per_shire, harts=per_shire * len(sh),
                    row_mean=round(sum(rows) / len(rows), 3), col_mean=round(sum(cols) / len(cols), 3))

    sets = {k: st(v) for k, v in MASKS.items()}
    sets["NULLA"] = st(MASKS["CEN8"])
    sets["NULLB"] = st(MASKS["CEN8"])
    sets["IDLE"] = dict(shires=[], mask="0x00000000", per_shire=0, harts=0,
                        row_mean=None, col_mean=None)
    assert abs(sets["N12"]["row_mean"] - sets["S12"]["row_mean"]) > 1.5
    assert sets["N12"]["col_mean"] == sets["S12"]["col_mean"]
    assert abs(sets["W12"]["col_mean"] - sets["E12"]["col_mean"]) > 2.5
    assert sets["W12"]["row_mean"] == sets["E12"]["row_mean"]

    def swap(name, title, a, b, dwell, cycles=7, kind="swap", predicted=None, rule=None,
             order=None):
        return dict(block=name, kind=kind, title=title, cycles=cycles, warmup_cycles=1,
                    dwell_s=dwell, arms=[a, b], contrast=[a, b], movie=True,
                    pre_idle_s=8.0, post_idle_s=8.0, order=order,
                    phases=[dict(set=a, seconds=dwell), dict(set=b, seconds=dwell)],
                    predicted=predicted or {}, pass_rule=rule)

    blocks = [
        dict(block="bloom", kind="bloom", title="The whole card breathes", cycles=1,
             warmup_cycles=0, movie=True, pre_idle_s=12.0, post_idle_s=20.0,
             phases=[dict(set="IDLE", seconds=12.0, idle=True),
                     dict(set="ALL32", seconds=30.0),
                     dict(set="IDLE", seconds=20.0, idle=True)],
             predicted=dict(dt_mk=[1500, 4500]), pass_rule="bloom_dt_p99_mk > 300"),
        swap("ns", "North <-> South, the row axis", "N12", "S12", 12.0,
             predicted=dict(amp_mk=[30, 300], axis="row"),
             rule="amp_mk > 30 and p < 0.05"),
        swap("we", "West <-> East, the column axis", "W12", "E12", 12.0, order="alternate",
             predicted=dict(amp_mk=[30, 300], axis="col"),
             rule="amp_mk > 30 and p < 0.05"),
        dict(block="corners", kind="sequence", title="Four corners, in a circle", cycles=4,
             warmup_cycles=1, dwell_s=8.0, movie=True, pre_idle_s=8.0, post_idle_s=8.0,
             arms=["B4NW", "B4NE", "B4SE", "B4SW"], contrast=["B4NW", "B4SE"],
             phases=[dict(set=s, seconds=8.0) for s in ("B4NW", "B4NE", "B4SE", "B4SW")],
             predicted=dict(amp_mk=[15, 200]), pass_rule="amp_mk > 15 and p < 0.05"),
        swap("null", "The null pair: the same shires on both arms", "NULLA", "NULLB", 12.0,
             kind="null", predicted=dict(amp_mk=[0, 0]), rule="p > 0.05"),
    ]
    return dict(experiment="E62", version=1, note="small protocol, for tests only",
                die=dict(grid=DIE_GRID, pitch_mm=3.72), sets=sets, blocks=blocks,
                caps=dict(abs_stop_c=90, cap_board_w=95), per_shire_w=1.3, idle_board_w=24.0)


# ---------------------------------------------------------------- the planted model

class Model:
    def __init__(self, a):
        self.mm_per_px = a.mm_per_px
        self.pitch_mm = a.pitch_mm
        self.k = a.pitch_mm / a.mm_per_px                       # full-res px per shire
        self.roll = math.radians(a.roll_deg)
        self.mirror = -1.0 if a.mirror else 1.0
        self.cx, self.cy = a.centre_x, a.centre_y
        self.sigma = a.sigma_mm / a.mm_per_px                   # full-res px
        self.amp = a.amp_mk_per_w
        self.tau = a.tau_s
        self.per_shire_w = a.per_shire_w

    def e_col(self):
        return np.array([math.cos(self.roll), math.sin(self.roll)]) * self.k

    def e_row(self):
        return np.array([-math.sin(self.roll), math.cos(self.roll)]) * self.k * self.mirror

    def xy(self, shire):
        r, c = SHIRE_RC[shire]
        u, v = c - 2.5, r - 2.5                                 # centred die coords, shire units
        p = np.array([self.cx, self.cy]) + u * self.e_col() + v * self.e_row()
        return float(p[0]), float(p[1])

    def blobs(self):
        """[32, H, W] float32: one unit-peak Gaussian per shire, at its image position."""
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        out = np.zeros((32, H, W), dtype=np.float32)
        for s in range(32):
            x, y = self.xy(s)
            out[s] = np.exp(-(((xx - x) ** 2 + (yy - y) ** 2) / (2.0 * self.sigma ** 2)))
        return out


# ---------------------------------------------------------------- the schedule

def runner_block_label(b, i):
    """The label `run_hm.py` writes into phases.jsonl: `str(b["name"] or "block<i>")`.

    It reads neither `block` nor `id`, so the registered protocol's E62-* blocks are logged as
    block0..block9.  Imitating the runner exactly is the point: a synthetic session that invented
    friendlier labels would hide the one mismatch most likely to break a real run.
    """
    v = b.get("name")
    return str(v) if isinstance(v, str) and v.strip() else "block%d" % i


def build_schedule(proto, a):
    """-> (phases, launches, blocks, t_end) with every time in seconds from the session start."""
    sets = proto.get("sets", {})
    t = a.lead_s
    phases, launches, blocks = [], [], []
    for bi, b in enumerate(proto["blocks"]):
        name = runner_block_label(b, bi)
        t += float(b.get("pre_idle_s", 8.0))
        b_start = t
        warm_n = int(b.get("warmup_cycles", 0))
        # run_hm.py:1476 runs `warmup_cycles + cycles` laps and flags the first warmup_cycles.
        # (The registered protocol's own conventions.cycles_rule says the opposite - that `cycles`
        # is the total - which is a live disagreement between the two; the runner is what actually
        # writes the session, so that is what is imitated here.)
        cycles = warm_n + int(b.get("cycles", 1))
        plist = b.get("phases") or [dict(set=s, seconds=b.get("dwell_s", 10.0))
                                    for s in b.get("arms", [])]
        alt = bool(b.get("alternate")) or b.get("order") == "alternate"
        rev = b.get("order") == "reverse"
        for cyc in range(cycles):
            order = list(plist)
            if rev or (alt and cyc % 2 == 1):
                order = order[::-1]
            for pi, ph in enumerate(order):
                secs = float(ph.get("seconds", ph.get("dwell_s", b.get("dwell_s", 10.0))))
                idle = bool(ph.get("idle")) or not sets.get(ph["set"], {}).get("shires")
                p0, p1 = t, t + secs
                rec = dict(block=name, cycle=cyc, phase=pi, set=ph["set"], idle=idle,
                           planned_start_ms=round(p0 * 1000), planned_end_ms=round(p1 * 1000),
                           n_launches=0, warmup=bool(cyc < warm_n), dwell_s=secs,
                           mask=sets.get(ph["set"], {}).get("mask"))
                if idle:
                    rec.update(t_first_start_ms=None, t_last_end_ms=None)
                    t = p1
                else:
                    sh = sets[ph["set"]]
                    lt, n = p0, 0
                    firsts, lasts = None, None
                    while lt < p1 - 0.25:
                        ls = lt
                        le = min(lt + a.launch_s, p1) if a.clip_launch else lt + a.launch_s
                        launches.append(dict(block=name, cycle=cyc, phase=pi, set=ph["set"],
                                             mask=sh.get("mask"), per_shire=sh.get("per_shire", 32),
                                             harts=sh.get("harts"), seconds=round(le - ls, 2),
                                             budget=a.launch_s + 1.2,
                                             t_start_ms=round(ls * 1000), t_end_ms=round(le * 1000),
                                             wall_s=round(le - ls, 3), rc=0, stderr_tail=""))
                        firsts = ls if firsts is None else firsts
                        lasts = le
                        n += 1
                        lt = le + a.gap_s
                    rec.update(n_launches=n, t_first_start_ms=round(firsts * 1000),
                               t_last_end_ms=round(lasts * 1000))
                    t = max(p1, lasts)
                phases.append(rec)
        blocks.append(dict(block=name, t_start_ms=round(b_start * 1000),
                           t_end_ms=round(t * 1000), status="done"))
        t += float(b.get("post_idle_s", 8.0))
    return phases, launches, blocks, t + a.tail_s


def power_intervals(launches, sets, per_shire_w):
    """-> sorted [(t0, t1, shire index array, watts per shire)] from the launch records."""
    out = []
    for l in launches:
        sh = sets.get(l["set"], {}).get("shires", [])
        if not sh:
            continue
        out.append((l["t_start_ms"] / 1000.0, l["t_end_ms"] / 1000.0,
                    np.asarray(sh, dtype=np.int64), per_shire_w))
    out.sort(key=lambda r: r[0])
    return out


# ---------------------------------------------------------------- writing the capture

def pack_frame(plane_u16, seq, mono_ns, wall_ns, fpa_c, framecount):
    info = np.zeros(INFO_WORDS, dtype="<u2")
    info[64] = framecount & 0xFFFF
    info[180] = framecount & 0xFFFF
    info[65] = 9000                                   # FPA NTC ADC, arbitrary but in range
    info[68] = int(np.clip(plane_u16.mean(), 0, 65535))
    info[168] = int(np.clip((34.85 + KELVIN_OFFSET) * 16, 0, 65535))
    info[174] = int(np.clip((45.60 + KELVIN_OFFSET) * 16, 0, 65535))
    info[176] = int(np.clip((fpa_c + KELVIN_OFFSET) * 16, 0, 65535))
    hdr = struct.pack(HDR_FMT, b"P3FZ", 1, seq, mono_ns, wall_ns,
                      600000 * framecount, 3 * framecount, (40 * framecount) % 65536,
                      W, H, float(fpa_c), 1, 1, 0)
    return hdr + info.tobytes() + plane_u16.astype("<u2").tobytes()


def synth(a):
    t_wall = time.time()
    with open(a.protocol) as f:
        proto = json.load(f)
    rng = np.random.default_rng(a.seed)
    os.makedirs(os.path.join(a.out, "cam"), exist_ok=True)
    os.makedirs(os.path.join(a.out, "logs"), exist_ok=True)
    os.makedirs(os.path.join(a.out, "truth", "red"), exist_ok=True)
    sets = proto.get("sets", {})
    per_shire_w = float(proto.get("per_shire_w", a.per_shire_w))
    a.per_shire_w = per_shire_w

    m = Model(a)
    phases, launches, blocks, t_end = build_schedule(proto, a)
    ivs = power_intervals(launches, sets, per_shire_w)
    epoch0 = a.epoch if a.epoch else float(int(time.time()))

    # ---- the static scene: ambient, a warmer card, a 0.7 degC fixed pattern
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    base_c = np.full((H, W), a.ambient_c, dtype=np.float32)
    x0, y0, x1, y1 = [int(v) for v in a.card.split(",")]
    card = (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1)
    base_c[card] += a.card_c
    fp = gblur(rng.standard_normal((H, W)).astype(np.float32), 12.0)
    fp = fp / (np.ptp(fp) + 1e-9) * a.fixed_pattern_c
    base_c = base_c + fp + rng.standard_normal((H, W)).astype(np.float32) * a.fixed_pixel_c
    base_mk = (base_c + KELVIN_OFFSET) * 1000.0

    # ---- the shiny component tops: a per-pixel gain on the signal only
    sh = gblur(rng.standard_normal((H, W)).astype(np.float32), 1.0)
    shiny = sh > np.percentile(sh, 100.0 - a.shiny_pct)
    gain = np.ones((H, W), dtype=np.float32)
    gain[shiny] = rng.uniform(a.shiny_gain_lo, a.shiny_gain_hi, int(shiny.sum())).astype(np.float32)

    # ---- the shutter events
    ffc_t, ffc_off, off_truth = [], [], []
    tf = a.ffc_period_s
    while tf < t_end - 2.0:
        g = gblur(rng.standard_normal((H, W)).astype(np.float32), 18.0)
        g = g / (np.std(g) + 1e-9) * a.ffc_spread_mk
        step = float(rng.uniform(-a.ffc_step_mk, a.ffc_step_mk))
        if abs(step) < 0.4 * a.ffc_step_mk:
            step = math.copysign(0.4 * a.ffc_step_mk, step)
        ffc_t.append(tf)
        ffc_off.append((g + step).astype(np.float32))
        off_truth.append(dict(t_s=round(tf, 3), step_mk_median=round(float(np.median(g + step)), 2),
                              note="step_mk_median is rewritten below to the jump the data really "
                                   "makes, which also includes the radial drift resetting"))
        tf += a.ffc_period_s * float(rng.uniform(0.85, 1.15))

    blobs = m.blobs()                                            # [32, H, W]
    radial = ((np.sqrt((xx - W / 2) ** 2 + (yy - H / 2) ** 2) / (0.5 * math.hypot(W, H))) - 0.5) * 2.0

    # ---- the clean cube, on the same 0.5 s grid the reducer will use
    nb = int(math.floor(t_end / a.bin_s)) + 1
    hb, wb = H // a.binning, W // a.binning
    cacc = np.zeros((nb, hb, wb), dtype=np.float64)
    ccnt = np.zeros(nb, dtype=np.int64)
    base_b = bin_plane(base_mk, a.binning)

    # ---- frames
    cam = open(os.path.join(a.out, "cam", "cam.p3rec"), "wb")
    dt = 1.0 / a.fps
    seq = 10_600_000
    framecount = 0
    state = np.zeros(32, dtype=np.float64)                       # the lagged power per shire
    iv_i = 0
    active_now = np.zeros(32, dtype=np.float64)
    nfr = 0
    cur_off = np.zeros((H, W), dtype=np.float32)
    next_ffc = 0
    t = 0.0
    prev_plane = None
    gaps = []
    while t <= t_end:
        # which launches are live
        active_now[:] = 0.0
        while iv_i < len(ivs) and ivs[iv_i][1] < t - 1e-9:
            iv_i += 1
        j = iv_i
        while j < len(ivs) and ivs[j][0] <= t:
            t0_, t1_, shs, wpr = ivs[j]
            if t0_ <= t <= t1_:
                active_now[shs] += wpr
            j += 1
        state += (active_now - state) * (1.0 - math.exp(-dt / m.tau))
        field = np.tensordot(state.astype(np.float32) * m.amp, blobs, axes=(0, 0))

        # the clean cube takes the field with no artefact at all
        k = int(math.floor(t / a.bin_s))
        if 0 <= k < nb:
            cacc[k] += base_b + bin_plane(field, a.binning)
            ccnt[k] += 1

        # the shutter: a frozen frame, a sequence gap, then a new offset map
        if next_ffc < len(ffc_t) and t >= ffc_t[next_ffc]:
            # What the data really jumps by, which is not the same as the new offset map.  The
            # radial post-shutter drift resets to zero here too, so the jump is the offset change
            # minus whatever radial had built up since the last shutter.  At the old 90 s default
            # that term had saturated and its spatial median was near zero, so recording only the
            # offset looked right; at the measured 12.5 s cadence it has not saturated, and a test
            # that compared the reducer against the offset alone was marking a correct measurement
            # wrong by up to 50 mK.
            lost = 0.0
            if next_ffc > 0:
                lost = a.radial_mk * (1.0 - math.exp(-(t - ffc_t[next_ffc - 1]) / 8.0)) * radial
            jump = ffc_off[next_ffc] - lost
            off_truth[next_ffc].update(
                step_mk_median=round(float(np.median(jump)), 2),
                offset_mk_median=off_truth[next_ffc]["step_mk_median"],
                radial_reset_mk_median=round(float(np.median(-lost)) if next_ffc else 0.0, 2),
                since_prev_s=round(t - ffc_t[next_ffc - 1], 2) if next_ffc else None)
            if prev_plane is not None and a.ffc_frozen:
                for _ in range(a.ffc_frozen):
                    mono = int((t + a.mono_skew) * 1e9)
                    blob = zlib.compress(pack_frame(prev_plane, seq, mono,
                                                    int((epoch0 + t - 0.345) * 1e9),
                                                    a.fpa_c, framecount), 1)
                    cam.write(struct.pack("<QI", int((epoch0 + t) * 1e9), len(blob)) + blob)
                    seq += 1
                    framecount += 1
                    nfr += 1
                    t += dt
            seq += a.ffc_gap_frames                              # the mechanical actuation
            gaps.append(dict(t_s=round(t, 3), frames=a.ffc_gap_frames))
            cur_off = cur_off + ffc_off[next_ffc]
            t += a.ffc_gap_frames * dt
            next_ffc += 1

        # Drift, and deliberately NOT a straight line.  The old plant was `rate * t` exactly, which
        # is the one drift a per-pixel linear detrend removes perfectly - so the analysis and the
        # plant agreed on a false premise and the recovery test could not see a detrend bias.  The
        # curve term is an FPA-style settling exponential plus a slow per-pixel tilt, neither of
        # which a line can absorb; what a line leaves behind is what lands on the later arm.
        drift = a.drift_mk_s * t
        if a.drift_curve_mk:
            drift = drift + a.drift_curve_mk * (1.0 - math.exp(-t / max(a.drift_curve_tau_s, 1e-3)))
            drift = drift + 0.35 * a.drift_curve_mk * (
                1.0 - math.exp(-t / max(a.drift_curve_tau_s, 1e-3))) * radial
        if next_ffc > 0:
            since = t - ffc_t[next_ffc - 1]
            drift = drift + a.radial_mk * (1.0 - math.exp(-since / 8.0)) * radial
        mk = base_mk + drift + cur_off + gain * field
        mk = mk + rng.standard_normal((H, W)).astype(np.float32) * a.noise_mk
        raw = np.clip(np.rint(mk / MK_PER_LSB / a.quantum) * a.quantum, 0, 65535).astype(np.uint16)
        mono = int((t + a.mono_skew) * 1e9)
        # the frame's content is `t`; its host stamp is when the blob landed, which is later by the
        # pipeline latency.  camera.md puts that at tens of ms (/health says lastFrameAgeMs 5), so
        # the default is 0.03 s - small, but planted so the chain is shown not to care rather than
        # assumed not to.
        host_ns = int((epoch0 + t + a.cam_latency_s + rng.normal(0.0, a.host_jitter_s)) * 1e9)
        blob = zlib.compress(pack_frame(raw, seq, mono, int((epoch0 + t - 0.345) * 1e9),
                                        a.fpa_c + 0.001 * t, framecount), 1)
        cam.write(struct.pack("<QI", host_ns, len(blob)) + blob)
        prev_plane = raw
        seq += 1
        framecount += 1
        nfr += 1
        t += dt
    cam.close()

    # ---- the runner's files
    t0ms = round(epoch0 * 1000)

    def ms(v):
        return None if v is None else int(v + t0ms)
    for p in phases:
        for key in ("planned_start_ms", "planned_end_ms", "t_first_start_ms", "t_last_end_ms"):
            p[key] = ms(p[key])
    for l in launches:
        l["t_start_ms"] = ms(l["t_start_ms"])
        l["t_end_ms"] = ms(l["t_end_ms"])
    for b in blocks:
        b["t_start_ms"] = ms(b["t_start_ms"])
        b["t_end_ms"] = ms(b["t_end_ms"])
    _jsonl(os.path.join(a.out, "phases.jsonl"), phases)
    _jsonl(os.path.join(a.out, "launches.jsonl"), launches)
    _jsonl(os.path.join(a.out, "blocks.jsonl"), blocks)
    _jsonl(os.path.join(a.out, "marks.jsonl"), [
        dict(t_ms=t0ms, kind="session_start", detail="synthetic"),
        dict(t_ms=t0ms + 10, kind="recorder_start", detail="cam/cam.p3rec"),
        dict(t_ms=round((epoch0 + t_end) * 1000), kind="session_stop", detail="done")])
    _tel(os.path.join(a.out, "tel.jsonl"), ivs, t_end, epoch0, a, proto)
    pr = json.dumps(proto, sort_keys=True).encode()
    with open(os.path.join(a.out, "protocol.json"), "w") as f:
        json.dump(proto, f, indent=1)
    with open(os.path.join(a.out, "session.json"), "w") as f:
        json.dump(dict(experiment=proto.get("experiment", "E62"),
                       protocol=os.path.abspath(a.protocol),
                       protocol_sha256=hashlib.sha256(pr).hexdigest(), protocol_copy=proto,
                       host="synthetic", user="synthetic", dry=True, git_head=None,
                       sha256=dict(synth_hm=_sha(os.path.abspath(__file__))),
                       caps=proto.get("caps", {}), t_start_ms=t0ms,
                       t_end_ms=round((epoch0 + t_end) * 1000), stop_reason="done"), f, indent=1)

    # ---- the clean RED and the truth
    cmk = np.full((nb, hb, wb), np.nan, dtype=np.float32)
    nz = ccnt > 0
    cmk[nz] = (cacc[nz] / ccnt[nz][:, None, None]).astype(np.float32)
    for j in np.nonzero(~nz)[0]:                                 # the same linear fill
        idx = np.nonzero(nz)[0]
        lo, hi = idx[idx < j], idx[idx > j]
        if len(lo) and len(hi):
            w_ = (j - lo[-1]) / float(hi[0] - lo[-1])
            cmk[j] = (1 - w_) * cmk[lo[-1]] + w_ * cmk[hi[0]]
        elif len(lo):
            cmk[j] = cmk[lo[-1]]
        elif len(hi):
            cmk[j] = cmk[hi[0]]
    red = os.path.join(a.out, "truth", "red")
    np.savez_compressed(os.path.join(red, "frames.npz"),
                        t_s=(np.arange(nb) + 0.5) * a.bin_s, mk=cmk,
                        n=np.minimum(ccnt, 32767).astype(np.int16),
                        ffc=np.zeros(nb, dtype=bool))
    np.save(os.path.join(red, "scene.npy"), base_c.astype(np.float32))
    with open(os.path.join(red, "ffc.json"), "w") as f:
        json.dump([], f)
    with open(os.path.join(red, "meta.json"), "w") as f:
        json.dump(dict(tool="synth_hm.py", clean=True, bins=nb, bin_s=a.bin_s,
                       binning=a.binning, shape=[hb, wb], fps=a.fps,
                       t_zero_epoch_s=epoch0), f, indent=1)
    for nm in ("session.json", "launches.jsonl", "phases.jsonl", "blocks.jsonl",
               "tel.jsonl", "marks.jsonl", "protocol.json"):
        with open(os.path.join(a.out, nm)) as src, open(os.path.join(red, nm), "w") as dst:
            dst.write(src.read())

    truth = dict(
        tool="synth_hm.py", seed=a.seed, fps=a.fps, frames=nfr, t_end_s=round(t_end, 3),
        epoch0=epoch0, bin_s=a.bin_s, binning=a.binning,
        map=dict(roll_deg=a.roll_deg, mirror=bool(a.mirror), centre_px=[a.centre_x, a.centre_y],
                 px_per_shire_full=round(m.k, 4), px_per_shire_binned=round(m.k / a.binning, 4),
                 mm_per_px=a.mm_per_px, pitch_mm=a.pitch_mm,
                 sigma_px_full=round(m.sigma, 3), sigma_px_binned=round(m.sigma / a.binning, 3),
                 sigma_mm=a.sigma_mm,
                 col_unit_xy=[round(v, 6) for v in (m.e_col() / m.k).tolist()],
                 row_unit_xy=[round(v, 6) for v in (m.e_row() / m.k).tolist()]),
        physics=dict(amp_mk_per_w=a.amp_mk_per_w, tau_s=a.tau_s, per_shire_w=per_shire_w,
                     drift_mk_s=a.drift_mk_s, drift_curve_mk=a.drift_curve_mk,
                     drift_curve_tau_s=a.drift_curve_tau_s, radial_mk=a.radial_mk,
                     drift_total_mk=round(a.drift_mk_s * t_end + a.drift_curve_mk, 1)),
        camera=dict(noise_mk=a.noise_mk, quantum_counts=a.quantum, latency_s=a.cam_latency_s,
                    mk_per_lsb=MK_PER_LSB, shiny_pct=a.shiny_pct,
                    shiny_gain=[a.shiny_gain_lo, a.shiny_gain_hi],
                    fixed_pattern_c=a.fixed_pattern_c),
        ffc=dict(n=len(ffc_t), period_s=a.ffc_period_s, gap_frames=a.ffc_gap_frames,
                 frozen_frames=a.ffc_frozen, events=off_truth),
        blocks=[_block_truth(b, sets, m, i) for i, b in enumerate(proto["blocks"])],
    )
    with open(os.path.join(a.out, "truth", "truth.json"), "w") as f:
        json.dump(truth, f, indent=1)
    np.save(os.path.join(a.out, "truth", "gain.npy"), gain)
    print("synth %s: %d frames @ %g fps, %.1f s, %d FFC, cam %.1f MB (%.1f s)"
          % (a.out, nfr, a.fps, t_end, len(ffc_t),
             os.path.getsize(os.path.join(a.out, "cam", "cam.p3rec")) / 1e6,
             time.time() - t_wall))
    return truth


def _block_truth(b, sets, m, bi=None):
    """What the block's arms should look like: the die displacement and its image direction."""
    arms = b.get("arms") or [p["set"] for p in b.get("phases", []) if not p.get("idle")]
    arms = [x for i, x in enumerate(arms) if x not in arms[:i]]
    bname = next((str(b[k]).strip() for k in ("block", "name", "id")
                  if isinstance(b.get(k), str) and b[k].strip()),
                 None if bi is None else "block%d" % bi)
    rc = {}
    for s in arms:
        shs = sets.get(s, {}).get("shires", [])
        if not shs:
            continue
        rc[s] = (float(np.mean([SHIRE_RC[x][0] for x in shs])),
                 float(np.mean([SHIRE_RC[x][1] for x in shs])))
    out = dict(block=bname, runner_label=runner_block_label(b, bi or 0),
               kind=b.get("kind"), arms=arms, n_arms=len(arms),
               cycles=b.get("cycles"), warmup_cycles=b.get("warmup_cycles", 0),
               cycles_run=int(b.get("warmup_cycles", 0)) + int(b.get("cycles", 1)),
               cycles_usable=int(b.get("cycles", 1)),
               order=b.get("order"), dwell_s=b.get("dwell_s"),
               arm_die_rc=rc, arm_dipole_deg={})
    if len(rc) >= 2:
        r0 = float(np.mean([v[0] for v in rc.values()]))
        c0 = float(np.mean([v[1] for v in rc.values()]))
        for s, (r, c) in rc.items():
            du, dv = c - c0, r - r0
            if abs(du) + abs(dv) < 1e-9:
                out["arm_dipole_deg"][s] = None
                continue
            vec = du * m.e_col() + dv * m.e_row()
            out["arm_dipole_deg"][s] = round(math.degrees(math.atan2(vec[1], vec[0])), 3)
            out.setdefault("arm_die_offset", {})[s] = [round(du, 4), round(dv, 4)]
    pair = b.get("contrast") or (arms[:2] if len(arms) >= 2 else None)
    if pair and all(p in rc for p in pair):
        du = rc[pair[0]][1] - rc[pair[1]][1]
        dv = rc[pair[0]][0] - rc[pair[1]][0]
        out["contrast"] = list(pair)
        out["contrast_die_offset"] = [round(du, 4), round(dv, 4)]
        if abs(du) + abs(dv) > 1e-9:
            vec = du * m.e_col() + dv * m.e_row()
            out["contrast_dipole_deg"] = round(math.degrees(math.atan2(vec[1], vec[0])), 3)
            out["contrast_shire_distance"] = round(math.hypot(du, dv), 4)
        else:
            out["contrast_dipole_deg"] = None
            out["contrast_shire_distance"] = 0.0
    return out


def _tel(path, ivs, t_end, epoch0, a, proto):
    """ettelem-shaped samples: board power, the minion-shire mean, the clock, at --tel-hz."""
    idle_w = float(proto.get("idle_board_w", 24.0))
    rows = []
    rng = np.random.default_rng(a.seed + 7)
    step = 1.0 / a.tel_hz
    t = 0.0
    while t <= t_end:
        w = idle_w
        for t0_, t1_, shs, wpr in ivs:
            if t0_ <= t <= t1_:
                w += len(shs) * wpr
        w += float(rng.normal(0, 0.25))
        die = 51.0 + 0.68 * (w - idle_w)
        mhz = 800 if die < 65 else (700 if die < 72 else 600)
        rows.append(dict(t_ms=round((epoch0 + t) * 1000), took_ms=22, since_reset_ms=1000,
                         board_w=round(w, 2),
                         sp=dict(board_avg_w=round(w, 2), board_min_w=round(idle_w, 2),
                                 board_max_w=round(w, 2), minion_c=[int(die), int(die) - 1,
                                                                    int(die) + 1],
                                 minion_mhz=[mhz, mhz, mhz], noc_mhz=[400, 400, 400]),
                         temp_c=dict(pmic=int(die + 3), ioshire=[int(die) + 1, int(die) - 2,
                                                                 int(die) + 2],
                                     minshire=[int(die), int(die) - 2, int(die) + 2]),
                         die_mv=dict(minion=614 if mhz >= 800 else 519),
                         mhz=dict(minion=mhz, noc=400, ddr=933)))
        t += step
    if a.tel_wrapped:
        rows = [dict(host_ms=r["t_ms"], line=json.dumps(r)) for r in rows]
    _jsonl(path, rows)


def _jsonl(path, rows):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--protocol")
    p.add_argument("--out")
    p.add_argument("--write-demo-protocol")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--fps", type=float, default=5.0, help="25 is the camera's rate; 5 keeps tests small")
    p.add_argument("--epoch", type=float, help="host epoch s of t=0 (default: now)")
    # geometry
    p.add_argument("--mm-per-px", type=float, default=0.156, help="full-resolution scale")
    p.add_argument("--pitch-mm", type=float, default=3.72)
    p.add_argument("--roll-deg", type=float, default=20.0, help="the planted camera roll")
    p.add_argument("--mirror", action="store_true", default=True, help="planted mirrored view")
    p.add_argument("--no-mirror", dest="mirror", action="store_false")
    p.add_argument("--centre-x", type=float, default=128.0)
    p.add_argument("--centre-y", type=float, default=96.0)
    p.add_argument("--sigma-mm", type=float, default=11.0, help="blur sigma (FWHM 2.355x)")
    # physics
    p.add_argument("--amp-mk-per-w", type=float, default=30.0, dest="amp_mk_per_w")
    p.add_argument("--tau-s", type=float, default=15.0)
    p.add_argument("--per-shire-w", type=float, default=1.3)
    p.add_argument("--drift-mk-s", type=float, default=6.0)
    p.add_argument("--drift-curve-mk", type=float, default=900.0,
                   help="a settling (non-linear) drift component, which a linear detrend cannot "
                        "remove; set 0 for the old straight-line plant")
    p.add_argument("--drift-curve-tau-s", type=float, default=240.0)
    p.add_argument("--cam-latency-s", type=float, default=0.03,
                   help="the frame's content is this much older than its host receive stamp")
    p.add_argument("--radial-mk", type=float, default=140.0, help="post-shutter radial drift")
    # camera
    p.add_argument("--noise-mk", type=float, default=34.0)
    p.add_argument("--quantum", type=int, default=4, help="counts per step (the live preset's 4)")
    p.add_argument("--ambient-c", type=float, default=40.3)
    p.add_argument("--card-c", type=float, default=1.2)
    p.add_argument("--card", default="40,30,215,165")
    p.add_argument("--fixed-pattern-c", type=float, default=0.7)
    p.add_argument("--fixed-pixel-c", type=float, default=0.05)
    p.add_argument("--shiny-pct", type=float, default=12.4)
    p.add_argument("--shiny-gain-lo", type=float, default=0.5)
    p.add_argument("--shiny-gain-hi", type=float, default=0.85)
    p.add_argument("--fpa-c", type=float, default=43.8)
    p.add_argument("--ffc-period-s", type=float, default=12.5,
                   help="the measured cadence on the real camera: 24 events in 300 s on the idle "
                        "capture, not the 90 s ceiling the header implies.  The old 90 s default "
                        "hid a detrend that invented a dipole on real frames, so it is 12.5 here")
    p.add_argument("--ffc-step-mk", type=float, default=300.0)
    p.add_argument("--ffc-spread-mk", type=float, default=60.0)
    p.add_argument("--ffc-gap-frames", type=int, default=10)
    p.add_argument("--ffc-frozen", type=int, default=1)
    p.add_argument("--mono-skew", type=float, default=123.4, help="phone monotonic clock offset, s")
    p.add_argument("--host-jitter-s", type=float, default=0.004)
    # schedule realisation
    p.add_argument("--launch-s", type=float, default=8.3, help="one heater process's wall time")
    p.add_argument("--gap-s", type=float, default=0.05)
    p.add_argument("--clip-launch", action="store_true", default=True,
                   help="the last launch of a phase stops at the phase end")
    p.add_argument("--no-clip-launch", dest="clip_launch", action="store_false")
    p.add_argument("--lead-s", type=float, default=6.0, help="camera running before the first block")
    p.add_argument("--tail-s", type=float, default=6.0)
    p.add_argument("--tel-hz", type=float, default=2.0)
    p.add_argument("--tel-wrapped", action="store_true", help="write tel as {host_ms, line}")
    p.add_argument("--bin-s", type=float, default=0.5)
    p.add_argument("--binning", type=int, default=2)
    a = p.parse_args(argv)
    if a.write_demo_protocol:
        with open(a.write_demo_protocol, "w") as f:
            json.dump(demo_protocol(), f, indent=1)
        print("wrote %s" % a.write_demo_protocol)
        return
    if not a.protocol or not a.out:
        p.error("--protocol and --out are required (or --write-demo-protocol)")
    synth(a)


if __name__ == "__main__":
    main()
