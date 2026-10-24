#!/usr/bin/env python3
"""E64 amendment A1: read the service processor's whole trace ring, binary records included.

    sptrace_full.py <dump.bin> [<dump.bin> ...]     every entry of each dump, new since the previous one

tools/claims-v3/dv2/sptrace_events.py walks the ring from its header to the write offset and stops at the first entry
that is not a printable string. On the 1.3.1 cards the governor writes a 16-byte binary power-status record
(Trace_Power_Status) next to its text lines, so that walk ends at the first operating-point change and loses every
later line (the 23 Oct smoke: 7-29 of 60-64 entries). This reader scans the whole ring at 8-byte steps instead, keeps
every entry that parses (a timestamp, a length that is a multiple of 8, and a NUL-terminated printable string, or a
16-byte record of type 14), and orders them by timestamp. Entries are kept by (timestamp, offset), so a dump taken
while the SP writes can show a torn entry at most once.

Entry kinds:
  power_up, power_down, power_idle, thermal_down, thermal_idle   the governor's CRITICAL lines (sptrace_events.PATTERNS)
  new_op      "New OP: Freq <MHz> MNN <mV> (V) SRM <mV> (V)": an operating point set (set_minion_operating_point)
  pstat       the binary power-status record: power (W), throttle state, power state, temperature (C), target MHz
  query_noise the lines a residency query for states 4-6 writes ("Unexpected power throtlling state", get_throttle_time)
  other       any other string

The binary record's layout was read off the 23 Oct smoke dumps against their neighbouring text lines (power 59 W at
"current pwr 59840", 54 C on a 54-55 C die, 700 MHz before "New OP: Freq 700"): after the 8-byte timestamp, a u32
length of 16, a u16 that is not set, a u16 type of 14, then u16 power W, u8 throttle state, u8 power state, u32
temperature C, u16 target MHz, and two bytes that are not set. Throttle states (device_mgmt_api_spec.h): 0 POWER_IDLE,
1 POWER_UP, 2 POWER_DOWN, 3 POWER_SAFE; higher values are the build's thermal states.
"""
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "dv2"))
import sptrace_events as spe  # noqa: E402

HEADER = 64
NEW_OP = re.compile(rb"New OP: Freq (\d+) MNN (\d+) \(V\) SRM (\d+)")
NOISE = re.compile(rb"Unexpected power throtlling state|get_throttle_time")
GOVERNOR = spe.GOVERNOR


def _printable(b):
    return len(b) > 0 and all(32 <= c < 127 or c in (9, 10, 13) for c in b)


def scan(buf):
    """Every entry in the ring, in timestamp order: dicts with ts, off, kind and fields."""
    if len(buf) < HEADER or struct.unpack_from("<I", buf, 0)[0] != spe.MAGIC:
        return None
    size = struct.unpack_from("<I", buf, 16)[0] or len(buf)
    size = min(size, len(buf))
    out, off = [], HEADER
    while off + 16 <= size:
        ts, n = struct.unpack_from("<QI", buf, off)
        if not (0 < n <= 512 and n % 8 == 0 and off + 16 + n <= size + 16) or ts == 0:
            off += 8
            continue
        if n == 16 and off + 32 <= size:
            typ = struct.unpack_from("<H", buf, off + 14)[0]
            if typ == 14:
                pw, ths, pws, temp, mhz = struct.unpack_from("<HBBIH", buf, off + 16)
                if 0 <= pw < 400 and 0 <= temp < 200 and 0 <= mhz <= 2000 and ths < 16:
                    out.append({"ts": ts, "off": off, "kind": "pstat", "power_w": pw, "throttle_state": ths,
                                "power_state": pws, "temp_c": temp, "mhz": mhz})
                    off += 32
                    continue
        if off + 16 + n > size:
            off += 8
            continue
        body = buf[off + 16:off + 16 + n]
        text = body.split(b"\0")[0]
        if b"\0" not in body or not _printable(text) or len(text) < 4:
            off += 8
            continue
        d = {"ts": ts, "off": off, "text": text.decode("latin-1").rstrip()}
        kind, vals = spe.classify_line(text)
        m = NEW_OP.search(text)
        if kind in GOVERNOR:
            d["kind"] = kind
            if kind in ("thermal_down", "thermal_idle"):
                d["T"], d["threshold"] = vals[0], vals[1]
            elif vals:
                d["pwr_mw"], d["tdp_mw"] = vals[0], vals[1]
        elif m:
            d["kind"], d["mhz"], d["mnn_mv"], d["srm_mv"] = "new_op", int(m.group(1)), int(m.group(2)), int(m.group(3))
        elif NOISE.search(text):
            d["kind"] = "query_noise"
        else:
            d["kind"] = "other"
        out.append(d)
        off += 16 + n
    seen, uniq = set(), []
    for e in sorted(out, key=lambda e: (e["ts"], e["off"])):
        k = (e["ts"], e["off"])
        if k not in seen:
            seen.add(k)
            uniq.append(e)
    return uniq


def since(prev, cur):
    """The entries of cur newer than every entry of prev."""
    if not prev:
        return list(cur)
    t0 = max(e["ts"] for e in prev)
    return [e for e in cur if e["ts"] > t0]


def main(argv):
    prev = None
    for p in argv:
        cur = scan(open(p, "rb").read())
        new = since(prev, cur) if prev is not None else cur
        print(f"== {os.path.basename(p)}: {len(cur)} entries, {len(new)} new")
        for e in new:
            if e["kind"] == "query_noise":
                continue
            print("  ", json.dumps({k: v for k, v in e.items() if k not in ("off",)}))
        prev = cur
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
