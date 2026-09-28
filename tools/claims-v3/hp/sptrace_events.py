#!/usr/bin/env python3
"""The service processor's governor lines from an `ettelem sptrace` dump, with their SP timestamps (DESIGN2 §3.2-3.3).

    sptrace_events.py --self-test                         the committed 22 Sep aifoundry3 ring + synthetic rings
    sptrace_events.py events <dump.bin>                   every entry as JSON lines (kind, ts, values, text)
    sptrace_events.py level <dump.bin>                    DEBUG | INFO | WARNING_OR_LOWER | EMPTY (the whole ring:
                                                          for the record only; INFO-era lines survive a switch)
    sptrace_events.py level-since <prev.bin> <cur.bin> [--begin]
                                                          the level from cur's entries newer than prev's (the rule
                                                          the blocks use): DEBUG | INFO | WARNING_OR_LOWER | UNKNOWN
    sptrace_events.py classify <p0.bin> <p1.bin> [--config config.json]
                                                          the R0 probe class: ALIVE | STUCK | SILENT (| ALIVE_CANDIDATE)
    sptrace_events.py overlap <prev.bin> <cur.bin>        exit 0 if the newest entry of prev reappears in cur

The dump is the SP's 4 KB trace ring: a 64-byte header (magic 0x76543210; word 3 is the offset of the next write,
word 4 the ring size), then entries of a u64 timestamp, a u32 string length, 4 unused bytes and the NUL-padded string.
The length is a multiple of **8** in the dumps of the 1.3.1 cards (56 and 64 in the 22 Sep aifoundry3 ring), so
tools/ettelem/parse_sptrace_voltage.py's ring_entries(), which requires a multiple of 16 (the DEBUG voltage lines),
walks none of them (tools/claims-v3/tel/reduce.py:1171-1172 notes the same). This module therefore walks the ring
itself: the entries written since the last wrap (header -> write offset), then the older entries that survive beyond
the write offset. The first of those usually lost its timestamp to the newest entry's tail (the ring wraps whole
entries), so it is kept with ts None ("partial"): it counts as a line, never as a timed event.

Line formats (identical in tpm-may2024.c, the 1.3.1 cards' closest source, and da192816a, card 1's 0.18.0):
  CRITICAL  Thermal throttle down event, current temperature: %u, threshold: %d          (TPM:673-674)
  CRITICAL  Thermal idle state event, current temperature %u, threshold %u               (TPM:2371-2372)
  CRITICAL  Power throttle down event, current pwr %u  tdp level: %u                      (TPM:866-867)
  CRITICAL  Power throttle up event, current pwr %u  tdp level: %u                        (TPM:880-881)
  CRITICAL  Power idle state event, current pwr %u  tdp level %u  (and, after 60b40c10f, without the numbers)
  INFO      Power Throttle event received. throttle_state: %d                             (TPM:2421)
  INFO      Host_Iface: Received DM request from host. / pc_vq_process_pending_command ... (the host's requests)
  DEBUG     MS nn Voltage [mV]: ...                                                       (pvt_controller.c)
"""
import json
import re
import struct
import sys

MAGIC, HEADER = 0x76543210, 64

PATTERNS = [
    ("thermal_down", re.compile(rb"Thermal throttle down event, current temperature: (\d+), threshold: (-?\d+)")),
    ("thermal_idle", re.compile(rb"Thermal idle state event, current temperature (\d+), threshold (-?\d+)")),
    ("power_down", re.compile(rb"Power throttle down event, current pwr (\d+)\s+tdp level: (\d+)")),
    ("power_up", re.compile(rb"Power throttle up event, current pwr (\d+)\s+tdp level: (\d+)")),
    ("power_idle", re.compile(rb"Power idle state event, current pwr (\d+)\s+tdp level (\d+)")),
    ("power_idle", re.compile(rb"Power idle state event")),
    ("received", re.compile(rb"Power Throttle event received\. throttle_state: (-?\d+)")),
    ("host", re.compile(rb"Host_Iface|pc_vq_process")),
    ("debug_voltage", re.compile(rb"MS\s*\d+ Voltage")),
]
GOVERNOR = {"thermal_down", "thermal_idle", "power_down", "power_up", "power_idle"}
POWER_START = {"power_down", "power_up"}
THERMAL = {"thermal_down", "thermal_idle"}


def _printable(b):
    return len(b) > 0 and all(32 <= c < 127 or c in (9, 10, 13) for c in b)


def _entry_at(buf, off, size):
    """(ts, n, text) if a whole, plausible entry starts at off, else None."""
    if off + 16 > size:
        return None
    ts, n, _ = struct.unpack_from("<QII", buf, off)
    if not (0 < n <= 512 and n % 8 == 0) or off + 16 + n > size:
        return None
    body = buf[off + 16:off + 16 + n]
    text = body.split(b"\0")[0]
    if not _printable(text) or b"\0" not in body:
        return None
    return ts, n, text


def ring_entries(buf):
    """[{ts, off, text, stale}] in time order (partial entries, ts None, first), or None if buf is not a ring."""
    if len(buf) < HEADER or struct.unpack_from("<I", buf, 0)[0] != MAGIC:
        return None
    wr, size = struct.unpack_from("<II", buf, 12)
    size = min(size or len(buf), len(buf))
    new, off = [], HEADER
    while off < min(wr, size):
        e = _entry_at(buf, off, size)
        if e is None:
            break
        new.append({"ts": e[0], "off": off, "text": e[2], "stale": False})
        off += 16 + e[1]
    stale = []
    if HEADER <= wr < size:
        tmin = min((e["ts"] for e in new), default=None)
        off = wr
        # the entry whose timestamp the newest entry's tail overwrote: its length word sits at the write offset
        if off + 8 <= size:
            n = struct.unpack_from("<I", buf, off)[0]
            body = buf[off + 8:off + 8 + n] if 0 < n <= 512 and n % 8 == 0 and off + 8 + n <= size else b""
            text = body.split(b"\0")[0]
            if body and _printable(text) and b"\0" in body:
                stale.append({"ts": None, "off": off - 8, "text": text, "stale": True, "partial": True})
                off += 8 + n
        while off + 16 <= size:
            e = _entry_at(buf, off, size)
            if e is None or (tmin is not None and not (0 < e[0] < tmin)):
                off += 8          # scan on: a torn tail of an older entry
                continue
            stale.append({"ts": e[0], "off": off, "text": e[2], "stale": True})
            off += 16 + e[1]
    timed = sorted([e for e in stale + new if e["ts"] is not None], key=lambda e: (e["ts"], e["off"]))
    return [e for e in stale if e["ts"] is None] + timed


def classify_line(text):
    for kind, rx in PATTERNS:
        m = rx.search(text)
        if m:
            vals = [int(g) for g in m.groups()]
            return kind, vals
    return "other", []


def events(buf):
    """Every entry with its kind and values. A buffer that is not a ring is read as text (ts None for every line)."""
    ents = ring_entries(buf)
    if ents is None:
        ents = [{"ts": None, "off": m.start(), "text": m.group(0), "stale": False}
                for m in re.finditer(rb"[^\n\0]{8,}", buf)]
    out = []
    for e in ents:
        kind, vals = classify_line(e["text"])
        d = {"kind": kind, "ts": e["ts"], "off": e["off"], "stale": e.get("stale", False),
             "partial": e.get("partial", False), "text": e["text"].decode("latin-1").rstrip()}
        if kind in ("thermal_down", "thermal_idle"):
            d["T"], d["threshold"] = vals[0], vals[1]
        elif kind in ("power_down", "power_up") or (kind == "power_idle" and vals):
            d["pwr_mw"], d["tdp_mw"] = vals[0], vals[1]
        elif kind == "received":
            d["state"] = vals[0]
        out.append(d)
    return out


def level(evs):
    """The level inference of DESIGN2 §3.2 step 2 from a dump's entries."""
    kinds = {e["kind"] for e in evs}
    if not evs:
        return "EMPTY"
    if "debug_voltage" in kinds:
        return "DEBUG"
    if "host" in kinds or "received" in kinds:
        return "INFO"
    return "WARNING_OR_LOWER"


def newest(evs):
    t = [e for e in evs if e["ts"] is not None]
    return max(t, key=lambda e: e["ts"]) if t else None


def overlap(prev, cur):
    """The coverage test: the newest entry of the previous dump reappears (same ts and text) in this one."""
    p = newest(prev)
    if p is None:
        return True          # nothing to lose
    return any(e["ts"] == p["ts"] and e["text"] == p["text"] for e in cur)


def since(prev, cur):
    """The entries of cur newer than prev's newest entry (all timed entries of cur if prev has none)."""
    p = newest(prev)
    t0 = p["ts"] if p else -1
    return [e for e in cur if e["ts"] is not None and e["ts"] > t0]


def level_since(prev, cur):
    """The level from the entries of cur NEWER than prev's newest entry only (review medium, 27 Sep): the 4 KB ring
    holds about 50 entries, so INFO-era Host_Iface lines survive a switch to WARNING until about 50 newer lines
    overwrite them, and the whole ring (level()) can read INFO on a card at WARNING. prev and cur are two dumps taken
    back to back (or around one launch). At INFO or DEBUG a dump request is itself logged (Host_Iface / pc_vq): if the SP
    logs it before copying the ring, cur's own line is new in cur; if after, prev's line first appears in cur. Either
    way an INFO card shows a host line in the delta, and a card at WARNING or lower none: an empty delta reads
    WARNING_OR_LOWER. Returns DEBUG | INFO | WARNING_OR_LOWER."""
    new = since(prev, cur)
    return level(new) if new else "WARNING_OR_LOWER"


def level_since_begin(prev, cur):
    """The level found at a block's start (the only restore target): level_since, except that a delta reading INFO
    while the ring still holds DEBUG voltage lines is UNKNOWN (a DEBUG card whose voltage lines missed the short delta,
    or an INFO card with stale DEBUG-era lines): WARNING is never set on an ambiguous level."""
    lv = level_since(prev, cur)
    if lv == "INFO" and any(e["kind"] == "debug_voltage" for e in cur):
        return "UNKNOWN"
    return lv


def classify(p0, p1, tdp_w=None, p0_ring=True):
    """The R0 probe class from the dumps before (p0) and after (p1) one light launch (DESIGN2 §3.2). The level is the
    one of the entries new since p0 (level_since); the whole-ring levels are kept for the record only."""
    lv0, lv1 = level(p0), level(p1)
    new = since(p0, p1)
    gov = [e for e in new if e["kind"] in GOVERNOR]
    rec = [e for e in new if e["kind"] == "received"]
    counts = {k: sum(1 for e in new if e["kind"] == k) for k in sorted({e["kind"] for e in new})}
    lvl = level_since(p0, p1) if p0_ring else "UNKNOWN"
    out = {"level_ring_p0": lv0, "level_ring_p1": lv1, "level": lvl, "level_rule": "new entries since p0",
           "new_entries": len(new), "counts": counts, "covered": overlap(p0, p1), "tdp_w": tdp_w}
    if not gov:
        out["class"] = "SILENT"
    elif (lvl if lvl != "UNKNOWN" else lv1) in ("INFO", "DEBUG"):     # p0 unreadable: the whole ring, as before
        first = min(e["ts"] for e in gov)
        out["class"] = "ALIVE" if any(e["ts"] > first for e in rec) else "STUCK"
    else:
        # at WARNING or lower the received line is invisible: STUCK on a zero-TDP card (aifoundry3), otherwise an
        # ALIVE candidate whose first thermal event must be followed by an idle event (DESIGN2 §3.2)
        out["class"] = "STUCK" if tdp_w == 0 else "ALIVE_CANDIDATE"
    return out


def fit_ticks(sp, anchors, lag_ms=(0.0, 400.0), rate_ms_per_tick=(1e-7, 1e-2)):
    """Fit host_ms = a + b * sp_ts from SP power events and host anchors (DESIGN2 §3.3, timing).

    sp: [(ts, kind)] with kind 'start' (Power throttle up/down: follows a kernel start within one SP pass) or 'end'
    (Power idle state event: follows the process end within one pass). anchors: [(host_ms, kind)] of the same kinds.
    Robust: every pair of nearby SP start events against every pair of nearby host starts proposes (a, b); the
    proposal that puts the most SP events within lag_ms after an anchor of their kind wins; then least squares on
    those inliers. Returns {a, b, n, inliers, resid_rms_ms, resid_max_ms} or None."""
    s_st = sorted(t for t, k in sp if k == "start")
    h_st = sorted(t for t, k in anchors if k == "start")
    if len(s_st) < 2 or len(h_st) < 2:
        return None
    anc = {"start": sorted(t for t, k in anchors if k == "start"), "end": sorted(t for t, k in anchors if k == "end")}
    import bisect

    def inliers(a, b):
        out = []
        for ts, k in sp:
            h = a + b * ts
            arr = anc.get(k, [])
            i = bisect.bisect_right(arr, h - lag_ms[0]) - 1
            if i >= 0 and lag_ms[0] <= h - arr[i] <= lag_ms[1]:
                out.append((ts, arr[i]))
        return out
    best = None
    for i in range(len(s_st)):
        for k in range(i + 1, min(i + 4, len(s_st))):
            for j in range(len(h_st)):
                for l in range(j + 1, min(j + 8, len(h_st))):
                    b = (h_st[l] - h_st[j]) / float(s_st[k] - s_st[i])
                    if not (rate_ms_per_tick[0] <= b <= rate_ms_per_tick[1]):
                        continue
                    a = h_st[j] + 100.0 - b * s_st[i]
                    n = len(inliers(a, b))
                    if best is None or n > best[0]:
                        best = (n, a, b)
    if best is None or best[0] < 2:
        return None
    _, a, b = best
    for _ in range(3):
        pts = inliers(a, b)
        if len(pts) < 2:
            break
        mx = sum(t for t, _ in pts) / len(pts)
        my = sum(h for _, h in pts) / len(pts)
        sxx = sum((t - mx) ** 2 for t, _ in pts)
        if sxx <= 0:
            break
        b = sum((t - mx) * (h - my) for t, h in pts) / sxx
        a = my - b * mx      # the SP lags its anchor by up to one pass: the offset absorbs the mean lag
    # residuals about the fitted line (the offset now holds the mean lag): every SP event that falls inside the
    # anchors' span, against the nearest anchor of its kind; one beyond 300 ms voids the session's TRIG-B (§3.3)
    lo = min(t for t, _ in anchors) - 1000.0
    hi = max(t for t, _ in anchors) + 1000.0
    res = []
    for ts, k in sp:
        h = a + b * ts
        arr = anc.get(k, [])
        if not arr or not (lo <= h <= hi):
            continue
        j = bisect.bisect_left(arr, h)
        near = [arr[x] for x in (j - 1, j) if 0 <= x < len(arr)]
        res.append(min((h - x for x in near), key=abs))
    if not res:
        return None
    rms = (sum(r * r for r in res) / len(res)) ** 0.5
    return {"a_ms": a, "b_ms_per_tick": b, "tick_hz": 1000.0 / b, "n_sp": len(sp), "n_in_span": len(res),
            "inliers_300ms": sum(1 for r in res if abs(r) <= 300), "resid_rms_ms": rms,
            "resid_max_ms": max(abs(r) for r in res)}


# ----------------------------------------------------------------------------------------------- TRIG-B
def trigb_evaluate(dumps, anchors, samples, runs, candidate=False):
    """TRIG-B (DESIGN2 §3.3) on one card's session.

    dumps:   [path] in the order taken: the idle baseline first (sp-idle.bin), then one after each run
    anchors: [(host_ms, 'start'|'end')]: each heater process's first kernel start and its end
    samples: [(t_ms, mean, high)] of every sampler line of the session, sorted
    runs:    [{'idx', 't0_ms', 't_end_ms'}] of the measured runs (for the first-event tests)
    candidate: the probe said ALIVE_CANDIDATE (found at WARNING): the first thermal event must be followed by an idle
               event, or the card is STUCK and TRIG-B is None.
    Returns a dict with the counts, the per-event judgements and 'holds' (True / False / None)."""
    import bisect
    out = {"dumps": len(dumps), "covered": 0, "uncovered": [], "events": [], "first_event_tests": [],
           "controls": 0, "holds": None, "why": None}
    evs, prev = [], None
    for p in dumps:
        try:
            cur = events(open(p, "rb").read())
        except Exception:
            out["uncovered"].append(p); prev = None; continue
        if prev is None:
            prev = cur
            continue
        if overlap(prev, cur):
            out["covered"] += 1
            evs += since(prev, cur)
        else:
            out["uncovered"].append(p)
        prev = cur
    sp = [(e["ts"], "start") for e in evs if e["kind"] in POWER_START] + \
         [(e["ts"], "end") for e in evs if e["kind"] == "power_idle"]
    fit = fit_ticks(sp, anchors) if sp and anchors else None
    out["tick_fit"] = fit
    if fit is None:
        out["why"] = "no SP tick fit (%d power lines, %d anchors)" % (len(sp), len(anchors))
        return out
    if fit["resid_max_ms"] > 300:
        out["why"] = "SP tick fit residual %.0f ms > 300 ms: the session's TRIG-B is void" % fit["resid_max_ms"]
        return out
    host = lambda ts: fit["a_ms"] + fit["b_ms_per_tick"] * ts
    therm = sorted([e for e in evs if e["kind"] in THERMAL], key=lambda e: e["ts"])
    if candidate:
        downs = [e for e in therm if e["kind"] == "thermal_down"]
        if downs and not any(e["kind"] == "thermal_idle" and e["ts"] > downs[0]["ts"] for e in therm):
            out["why"] = "ALIVE_CANDIDATE reclassified STUCK: the first thermal down event has no idle event after it"
            out["reclassified"] = "STUCK"
            return out
    ts_s = [s[0] for s in samples]
    for e in therm:
        h = host(e["ts"])
        i0, i1 = bisect.bisect_left(ts_s, h - 500), bisect.bisect_right(ts_s, h + 500)
        win = samples[i0:i1]
        m = [s[1] for s in win if s[1] is not None]
        hi = [s[2] for s in win if s[2] is not None]
        if not m or not hi:
            out["events"].append({"kind": e["kind"], "T": e["T"], "host_ms": h, "judged": False})
            continue
        T = e["T"]
        disc = max(hi) >= max(m) + 2
        if e["kind"] == "thermal_down":
            h1 = T >= 66 and any(abs(T - x) <= 1 for x in m)
        else:
            h1 = T <= 65 and any(abs(T - x) <= 1 for x in m) and max(m) >= 65
        h1p = T >= max(m) + 2
        out["events"].append({"kind": e["kind"], "T": T, "host_ms": h, "judged": True, "discriminating": disc,
                              "H1": h1, "H1p": h1p, "mean_range": [min(m), max(m)], "high_max": max(hi)})
    downs_h = [host(e["ts"]) for e in therm if e["kind"] == "thermal_down"]
    for r in runs:
        t0, t1 = r["t0_ms"], r["t_end_ms"]
        pre = [s for s in samples if s[0] < t0][-3:]
        rearmed = len(pre) == 3 and all(s[2] is not None and s[2] <= 65 for s in pre)
        tm = next((s[0] for s in samples if s[0] >= t0 and s[1] is not None and s[1] >= 66), None)
        th = next((s[0] for s in samples if s[0] >= t0 and s[2] is not None and s[2] >= 66), None)
        fd = next((x for x in downs_h if t0 <= x <= t1 + 10000), None)
        rec = {"idx": r.get("idx"), "rearmed": rearmed, "t_m": tm, "t_hi": th, "first_down": fd}
        if rearmed and fd is not None:
            f1 = tm is not None and tm - 300 <= fd <= tm + 600
            f1p = th is not None and th - 300 <= fd <= th + 600
            rec.update(fits_H1=f1, fits_H1p=f1p, fits_H1p_only=f1p and not f1)
        # the control observation (B-neg): high >= 67 for >= 1 s while the mean read <= 64, and no down event then
        if rearmed:
            span = [s for s in samples if t0 <= s[0] <= t1 + 10000]
            run_start = None
            for s in span:
                ok = s[2] is not None and s[2] >= 67 and s[1] is not None and s[1] <= 64
                if ok and run_start is None:
                    run_start = s[0]
                if (not ok or s is span[-1]) and run_start is not None:
                    end = s[0]
                    if end - run_start >= 1000 and not any(run_start <= x <= end for x in downs_h):
                        out["controls"] += 1
                    run_start = None
        out["first_event_tests"].append(rec)
    D = [e for e in out["events"] if e.get("judged") and e["discriminating"]]
    n1 = sum(1 for e in D if e["H1"])
    n1p = sum(1 for e in D if e["H1p"])
    fe1p = sum(1 for r in out["first_event_tests"] if r.get("fits_H1p_only"))
    out.update(discriminating=len(D), h1_consistent=n1, h1p_consistent=n1p, first_event_h1p=fe1p,
               first_event_tests_n=sum(1 for r in out["first_event_tests"] if "fits_H1" in r))
    if D and n1p >= 0.5 * len(D) or fe1p >= 2:
        out["holds"] = False
    elif len(D) >= 5 and n1 >= 0.9 * len(D) and n1p <= 1 and fe1p == 0:
        out["holds"] = True
    else:
        out["holds"] = None
        out["why"] = "%d discriminating events (need >= 5 with >= 90%% H1-consistent)" % len(D)
    return out


# ----------------------------------------------------------------------------------------------- writing rings
def build_ring(entries, size=4096, total=8192, flags=0x82000002):
    """A ring as the SP writes it: entries [(ts, text)] in order, wrapping whole entries to the header."""
    buf = bytearray(total)
    off = HEADER
    for ts, text in entries:
        b = text.encode() + b"\0" if isinstance(text, str) else text + b"\0"
        b += b"\0" * (-len(b) % 8)
        if off + 16 + len(b) > size:
            off = HEADER
        struct.pack_into("<QII", buf, off, ts, len(b), 0)
        buf[off + 16:off + 16 + len(b)] = b
        off += 16 + len(b)
    struct.pack_into("<16I", buf, 0, MAGIC, 0x60000, 0x20000, off, size, flags, *[0] * 10)
    return bytes(buf)


def self_test(repo_root=None):
    import os
    root = repo_root or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
    path = os.path.join(root, "docs/reports/data/2026-09-22-cards/sptrace-aifoundry3.bin")
    buf = open(path, "rb").read()
    ev = events(buf)
    kinds = [e["kind"] for e in ev]
    n_down, n_idle = kinds.count("power_down"), kinds.count("power_idle")
    assert (n_down, n_idle) == (26, 27), (n_down, n_idle)
    assert len(re.findall(rb"throttle down event", buf)) == 26 and len(re.findall(rb"idle state event", buf)) == 27
    timed = [e for e in ev if e["ts"] is not None]
    assert len(timed) == 52 and sum(e["partial"] for e in ev) == 1, (len(timed), sum(e["partial"] for e in ev))
    assert all(e["tdp_mw"] == 0 for e in ev if e["kind"] in ("power_down",)), "aifoundry3's TDP is 0"
    assert level(ev) == "WARNING_OR_LOWER"
    ts = [e["ts"] for e in timed]
    assert ts == sorted(ts)
    # alternation: in time order the timed lines alternate down/idle (one power episode per launch)
    seq = [e["kind"] for e in timed]
    alt = sum(1 for x, y in zip(seq, seq[1:]) if x != y)
    print("22 Sep aifoundry3 ring: %d power_down + %d power_idle lines (%d timed, 1 partial), level %s, "
          "%d of %d consecutive pairs alternate, ts span %d ticks" % (n_down, n_idle, len(timed), level(ev), alt,
                                                                       len(seq) - 1, ts[-1] - ts[0]))
    # the V3 INFO-level dumps of 22 Sep aifoundry2: host lines, no governor line -> INFO, and SILENT against itself
    b2 = open(os.path.join(root, "docs/reports/data/2026-09-22-cards/sptrace-aifoundry2.bin"), "rb").read()
    e2 = events(b2)
    assert level(e2) == "INFO" and not any(e["kind"] in GOVERNOR for e in e2)
    # synthetic rings: ALIVE, STUCK, SILENT, wrap and overlap
    host = "Host_Iface: Received DM request from host.\n"
    p0 = build_ring([(1000 + i, host) for i in range(5)])
    alive = build_ring([(1000 + i, host) for i in range(5)] + [
        (2000, "Power throttle up event, current pwr 42000  tdp level: 65000\n"),
        (2001, "Power Throttle event received. throttle_state: 2\n"),
        (2500, "Power idle state event, current pwr 30000  tdp level 65000\n"),
        (2501, "Power Throttle event received. throttle_state: 0\n"), (2600, host)])
    stuck = build_ring([(1000 + i, host) for i in range(5)] + [
        (2000, "Power throttle down event, current pwr 35000  tdp level: 0\n"), (2600, host)])
    silent = build_ring([(1000 + i, host) for i in range(7)])
    assert classify(events(p0), events(alive))["class"] == "ALIVE"
    assert classify(events(p0), events(stuck))["class"] == "STUCK"
    assert classify(events(p0), events(silent))["class"] == "SILENT"
    warn = build_ring([(2000, "Power throttle down event, current pwr 35000  tdp level: 0\n")])
    assert classify([], events(warn), tdp_w=0)["class"] == "STUCK"
    assert classify([], events(warn), tdp_w=65)["class"] == "ALIVE_CANDIDATE"
    # the level from new entries only (review medium): a ring at WARNING that still holds 10 INFO-era host lines reads
    # INFO as a whole (the old rule) but WARNING_OR_LOWER from the entries new since the previous dump
    crit = "Power throttle down event, current pwr 35000  tdp level: 65000\n"
    info_era = [(1000 + i, host) for i in range(10)]
    w0 = build_ring(info_era + [(1100, crit)])
    w1 = build_ring(info_era + [(1100, crit), (1200, crit), (1300, crit)])
    assert level(events(w1)) == "INFO" and level_since(events(w0), events(w1)) == "WARNING_OR_LOWER"
    assert level_since(events(w0), events(w0)) == "WARNING_OR_LOWER"            # nothing new: no host line either
    i1 = build_ring(info_era + [(1100, crit), (1200, host)])                      # INFO: the dump request is logged
    assert level_since(events(w0), events(i1)) == "INFO"
    dbg = "MS 12 Voltage [mV]: 525 0 0 0\n"
    d1 = build_ring(info_era + [(1100, crit), (1200, host), (1201, dbg)])
    assert level_since(events(w0), events(d1)) == "DEBUG"
    stale_dbg = build_ring([(900, dbg)] + info_era + [(1100, crit), (1200, host)])
    assert level_since(events(w0), events(stale_dbg)) == "INFO" and \
        level_since_begin(events(w0), events(stale_dbg)) == "UNKNOWN"
    # the probe on a card at WARNING with INFO-era lines in its ring: ALIVE_CANDIDATE (tdp 65), not STUCK
    p1w = build_ring(info_era + [(2000, crit)])
    c = classify(events(build_ring(info_era)), events(p1w), tdp_w=65)
    assert c["level"] == "WARNING_OR_LOWER" and c["class"] == "ALIVE_CANDIDATE" and c["level_ring_p1"] == "INFO", c
    # a ring that wraps many times: the newest entries are all found, in order, and the stale ones are older
    many = [(5000 + 10 * i, "Thermal throttle down event, current temperature: %d, threshold: 65\n" % (60 + i % 9))
            for i in range(200)]
    r = build_ring(many)
    ev = events(r)
    tt = [e["ts"] for e in ev if e["ts"] is not None]
    assert tt == sorted(tt) and tt[-1] == many[-1][0] and all(e["kind"] == "thermal_down" for e in ev)
    assert overlap(events(build_ring(many[:150])), ev) is False      # 50 entries later the old newest is overwritten
    assert overlap(events(build_ring(many[:195])), ev) is True
    # tick fit: SP ticks at 40 MHz, host starts every 3 s, the SP logs 50-150 ms after each anchor
    import random
    rng = random.Random(1)
    h0, sp, anc = 1790000000000.0, [], []
    for i in range(12):
        hs, he = h0 + 3000 * i, h0 + 3000 * i + 2500
        anc += [(hs, "start"), (he, "end")]
        sp += [(int((hs + rng.uniform(50, 150) - h0 + 7e5) * 40000), "start"),
               (int((he + rng.uniform(50, 150) - h0 + 7e5) * 40000), "end")]
    f = fit_ticks(sp, anc)
    assert f and abs(f["tick_hz"] - 4e7) / 4e7 < 1e-3 and f["resid_max_ms"] < 100, f
    print("self-test ok: 22 Sep ring (26 down, 27 idle), INFO inference on the aifoundry2 ring, ALIVE/STUCK/SILENT/"
          "ALIVE_CANDIDATE, the level from new entries only (INFO-era lines at WARNING, DEBUG, stale DEBUG), wrap and "
          "overlap, tick fit %.4g Hz (max residual %.0f ms)" % (f["tick_hz"], f["resid_max_ms"]))


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "--self-test":
        self_test()
        return 0
    if argv[0] == "events":
        for e in events(open(argv[1], "rb").read()):
            print(json.dumps(e))
        return 0
    if argv[0] == "level":
        print(level(events(open(argv[1], "rb").read())))
        return 0
    if argv[0] == "level-since":
        # level-since <prev.bin> <cur.bin> [--begin]: UNKNOWN if either dump is missing or is not a ring
        try:
            bp, bc = open(argv[1], "rb").read(), open(argv[2], "rb").read()
        except Exception:
            print("UNKNOWN")
            return 0
        if ring_entries(bp) is None or ring_entries(bc) is None:
            print("UNKNOWN")
            return 0
        f = level_since_begin if "--begin" in argv[3:] else level_since
        print(f(events(bp), events(bc)))
        return 0
    if argv[0] == "classify":
        tdp = None
        if "--config" in argv:
            try:
                tdp = json.load(open(argv[argv.index("--config") + 1])).get("tdp_w")
            except Exception:
                tdp = None
        b0 = open(argv[1], "rb").read() if argv[1] != "-" else None
        p0 = events(b0) if b0 is not None else []
        p0_ring = b0 is None or ring_entries(b0) is not None
        print(json.dumps(classify(p0, events(open(argv[2], "rb").read()), tdp, p0_ring=p0_ring)))
        return 0
    if argv[0] == "overlap":
        ok = overlap(events(open(argv[1], "rb").read()), events(open(argv[2], "rb").read()))
        print("covered" if ok else "NOT covered")
        return 0 if ok else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
