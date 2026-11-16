#!/usr/bin/env python3
"""E198's kit (Q191, lane kit-e198, Sun 15 Nov 2026, before any E198 datum): THE GUARD between the X04 host's standard output and the
unchanged runner's X04 filter (E198.md sections 3 and 18.4; CONTEXT section 116's lesson). aifoundry1's device runtime prints its line
`Opening device <n>` on a host's standard output when the host opens card <n>; on Sun 15 Nov 2026 it fell INSIDE the ledger host's JSON
line (1a4bc1e3's smoke stdout). The unchanged runner keeps every line that begins `X04 {` and gives it to json.loads with no guard
(run_x04.py lines 540-542), so a runtime line inside an X04 line would raise there and end the sitting. x04host_e198.sh runs the built host
with its standard output to a raw file, then this filter writes that output with every runtime line removed, E191 kit note 2's
drop_runtime exactly: the exact text `Opening device <digits>` WITH its newline, wherever it fell (at a line's start, or inside a line).
An X04 line is one JSON object on one line, so it holds no raw newline and the removal never cuts into the host's own text. Nothing else
changes: the bytes left are the host's, in order. The raw file stays beside, every runtime line in it.

    python3 -I -B dropruntime_e198.py filter RAW INDEX SEQ RC     the host's output with runtime lines dropped, to stdout; one JSON line
                                                                  appended to INDEX (seq, rc, bytes, the dropped lines, what is left that
                                                                  is neither an X04 line nor empty, 'X04 {' not at a line's start)
    python3 -I -B dropruntime_e198.py facts INDEX                 the index summed (the collection's facts)
Standard library only. Exit 0 (filter: also when the raw file is unreadable: nothing is printed and the index says so). SPDX-License-Identifier: Apache-2.0
"""
import json
import re
import sys

RUNTIME = re.compile(rb"Opening device ([0-9]+)\n")


def drop_runtime(raw):
    """(clean bytes, [the card numbers of the dropped runtime lines, in order])."""
    dropped = [int(m.group(1)) for m in RUNTIME.finditer(raw)]
    return RUNTIME.sub(b"", raw), dropped


def leftovers(clean):
    """What a clean stream still holds that the runner would not read as an X04 record: (other non-empty lines, 'X04 {' found not at a
    line's start, 'Opening device' text left)."""
    other = sum(1 for ln in clean.split(b"\n") if ln.strip() and not ln.startswith(b"X04 {"))
    mid = sum(1 for ln in clean.split(b"\n") if b"X04 {" in ln[1:])
    left = clean.count(b"Opening device")
    return other, mid, left


def filter_main(raw_path, index_path, seq, rc):
    try:
        with open(raw_path, "rb") as f:
            raw = f.read()
        ok = True
    except OSError:
        raw, ok = b"", False
    clean, dropped = drop_runtime(raw)
    sys.stdout.buffer.write(clean)
    sys.stdout.buffer.flush()
    other, mid, left = leftovers(clean)
    row = {"seq": seq, "rc": rc, "raw_read": ok, "bytes_raw": len(raw), "bytes_clean": len(clean), "runtime_dropped": dropped,
           "x04_lines": sum(1 for ln in clean.split(b"\n") if ln.startswith(b"X04 {")), "other_lines": other,
           "x04_not_at_start": mid, "opening_text_left": left}
    try:
        with open(index_path, "a") as f:
            f.write(json.dumps(row, separators=(",", ":")) + "\n")
    except OSError:
        pass
    return 0


def facts(index_path):
    rows = []
    try:
        with open(index_path) as f:
            rows = [json.loads(x) for x in f if x.startswith("{")]
    except OSError:
        pass
    out = {"device_processes": len(rows), "runtime_lines_dropped": sum(len(r["runtime_dropped"]) for r in rows),
           "runtime_cards": sorted({c for r in rows for c in r["runtime_dropped"]}),
           "x04_lines": sum(r["x04_lines"] for r in rows), "other_lines": sum(r["other_lines"] for r in rows),
           "x04_not_at_start": sum(r["x04_not_at_start"] for r in rows),
           "opening_text_left": sum(r["opening_text_left"] for r in rows),
           "raw_unread": sum(1 for r in rows if not r["raw_read"])}
    print(json.dumps(out, sort_keys=True))
    return 0


def main(argv):
    if len(argv) == 5 and argv[0] == "filter":
        return filter_main(argv[1], argv[2], argv[3], int(argv[4]) if argv[4].lstrip("-").isdigit() else argv[4])
    if len(argv) == 2 and argv[0] == "facts":
        return facts(argv[1])
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
