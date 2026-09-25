#!/usr/bin/env python3
"""Per-shire on-die voltages from a service-processor trace dump (`ettelem sptrace <out.bin>`).

    python3 tools/ettelem/parse_sptrace_voltage.py SP.bin > per-shire-voltage-idle.json
    python3 tools/ettelem/parse_sptrace_voltage.py --self-test

With the SP's log level at DEBUG (`ettelem loglevel debug`), the firmware's per-pass power update prints one line per
minion shire (the GET_MINION_VM macro in ServiceProcessorBL2/driver/pvt_controller.c, et-platform 353f20e):

    MS %2d Voltage [mV]: VDD_MNN: %d [%d, %d] VDD_SRAM: %d [%d, %d] VDD_NOC: %d [%d, %d]

current, then the monitor's hardware low and high since the last stats reset, for the minion, SRAM and mesh rails.
The same macro prints "MS nn bad. skipping." and "... Sample fault ..." lines; they carry no values and are ignored.

The dump is the SP's 4 KB trace ring: a 64-byte header (magic 0x76543210; word 3 is the offset of the next write,
word 4 the buffer size), then entries of a u64 timestamp, a u32 string length (a multiple of 16), 4 unused bytes and
the string. The ring wraps, so the lines of one pass can sit on both sides of the write offset and a partly
overwritten line can remain near the end. This script orders the entries by timestamp, splits the voltage lines into
passes (a pass restarts when the shire number does not increase), and takes the latest pass in which all 34 minion
shires printed. A shire missing from every complete pass falls back to its latest line, with a warning on stderr.
A file without the ring header (for example the output of `strings`) is read line by line in file order.

Output: {"<shire>": {"mnn": [now, low, high], "sram": [...], "noc": [...]}} in mV, keys in the order the lines sit
in the file (the order `strings sp.bin` lists them), written with json.dumps(indent=0) and no final newline.

Run on the recovered 20 September traces (docs/reports/data/2026-09-20-power-aifoundry2/raw/sp1.bin, sp2.bin and
sp3.bin, three dumps about 0.3 s apart), sp1.bin reproduces the committed per-shire-voltage-idle.json byte for byte;
sp2.bin and sp3.bin are later passes whose current readings differ from it by 1 mV in a few cells, with identical lows
and highs (--compare prints the differences).
"""
import argparse
import json
import re
import struct
import sys

LINE = re.compile(rb"MS\s*(\d+) Voltage \[mV\]: VDD_MNN: (\d+) \[(\d+), (\d+)\] VDD_SRAM: (\d+) \[(\d+), (\d+)\]"
                  rb" VDD_NOC: (\d+) \[(\d+), (\d+)\]")
MAGIC, HEADER, NSHIRES = 0x76543210, 64, 34
FMT = ("MS %2d Voltage [mV]: VDD_MNN: %d [%d, %d] VDD_SRAM: %d [%d, %d] VDD_NOC: %d [%d, %d]\n")  # firmware format


def ring_entries(buf):
    """[(timestamp, file_offset, bytes)] for every whole entry of an SP trace ring, or None if buf is not one."""
    if len(buf) < HEADER or struct.unpack_from("<I", buf, 0)[0] != MAGIC:
        return None
    wr, size = struct.unpack_from("<II", buf, 12)
    size = min(size or len(buf), len(buf))

    def walk(off, stop):
        out = []
        while off + 16 <= stop:
            ts, n, _ = struct.unpack_from("<QII", buf, off)
            if not (0 < n <= 512 and n % 16 == 0) or off + 16 + n > size:
                break
            out.append((ts, off, buf[off + 16:off + 16 + n].split(b"\0")[0]))
            off += 16 + n
        return out
    seen, out = set(), []
    for e in walk(HEADER, size) + (walk(wr, size) if HEADER <= wr < size else []):
        if e[1] not in seen:
            seen.add(e[1]); out.append(e)
    return sorted(out)


def records(buf):
    """Voltage records [(order_key, file_offset, shire, values)] in time order (ring) or file order (plain text)."""
    ents = ring_entries(buf)
    if ents is None:
        ents = [(m.start(), m.start(), m.group(0)) for m in LINE.finditer(buf)]
    out = []
    for ts, off, s in ents:
        m = LINE.search(s)
        if m:
            g = [int(x) for x in m.groups()]
            out.append((ts, off, g[0], {"mnn": g[1:4], "sram": g[4:7], "noc": g[7:10]}))
    return out


def parse(buf, warn=sys.stderr):
    recs = records(buf)
    passes, cur, last = [], [], None
    for r in recs:
        if last is not None and r[2] <= last:
            passes.append(cur); cur = []
        cur.append(r); last = r[2]
    if cur:
        passes.append(cur)
    full = [p for p in passes if {r[2] for r in p} >= set(range(NSHIRES))]
    if full:
        chosen = {r[2]: r for r in full[-1]}
    else:  # per-shire fallback: each shire's latest line, which may mix passes
        print("warning: no pass has all %d shires; using each shire's latest line" % NSHIRES, file=warn)
        chosen = {r[2]: r for r in recs}
    missing = sorted(set(range(NSHIRES)) - set(chosen))
    if missing:
        print("warning: no voltage line for shires %s" % missing, file=warn)
    return {str(r[2]): r[3] for r in sorted(chosen.values(), key=lambda r: r[1])}


def self_test():
    vals = [(s, 517 + s % 5, 513 + s % 3, 520 + s % 3, 703 + s % 4, 701, 707, 483 + s % 3, 482, 487) for s in range(NSHIRES)]
    lines = [FMT % v for v in vals]
    # a ring: header, the pass split across the write offset (shires 20..33 first in the file), noise lines
    def ent(ts, s):
        b = s.encode() + b"\0"
        b += b"\0" * (-len(b) % 16)
        return struct.pack("<QII", ts, len(b), 0) + b
    body = b"".join(ent(1000 + k, lines[k]) for k in range(20, NSHIRES))
    body += ent(2000, "MS 5 bad. skipping.\r\n")
    body += ent(2001, "MS 7 Voltage [mV]: VDD_MNN: Sample fault VDD_SRAM: Sample fault VDD_NOC: Sample fault\n")
    wr = HEADER + len(body)
    body += ent(10, "Updating the periodically sampled parameters: dm_task_entry\n")
    body += b"".join(ent(900 + k, lines[k]) for k in range(20))
    buf = struct.pack("<16I", MAGIC, 0x60000, 0x20000, wr, HEADER + len(body) + 32, 2, *[0] * 10) + body + b"\xff" * 32
    got = parse(buf)
    want = {str(v[0]): {"mnn": list(v[1:4]), "sram": list(v[4:7]), "noc": list(v[7:10])} for v in vals}
    assert got == want, "ring parse differs"
    assert list(got)[:2] == ["20", "21"], "keys not in file order"
    txt = "".join(lines).encode()
    assert parse(txt) == want, "text parse differs"
    print("self-test ok: %d shires from a wrapped ring and from plain text" % NSHIRES)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("trace", nargs="?", help="ettelem sptrace dump (or any text holding the lines)")
    ap.add_argument("--self-test", action="store_true", help="parse lines built from the firmware format string")
    ap.add_argument("--compare", metavar="JSON", help="print the cells that differ from this voltage map")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.trace:
        ap.error("a trace file is required")
    d = parse(open(a.trace, "rb").read())
    if a.compare:
        ref = json.load(open(a.compare))
        diff = [(k, rail, ref.get(k, {}).get(rail), d[k][rail]) for k in d for rail in ("mnn", "sram", "noc")
                if ref.get(k, {}).get(rail) != d[k][rail]]
        for k, rail, r, v in diff:
            print("shire %s %s: %s -> %s" % (k, rail, r, v))
        print("%d differing cells of %d" % (len(diff), 3 * len(d)))
        return
    sys.stdout.write(json.dumps(d, indent=0))


if __name__ == "__main__":
    main()
