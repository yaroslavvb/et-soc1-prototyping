#!/usr/bin/env python3
"""E191's test doubles, v2 (KIT.md.dated-note-2.md, Q184, Sun 15 Nov 2026, PST: after E189's data commit fa9098c4 of Sat 14 Nov 2026,
20:34:12 PST, and after E191's first session stopped at its smoke gate (1a4bc1e3), before any E191 pass datum): fake_card_e191.py
(eb1ac923, unchanged beside it: every double and mode of it is this module's by import) with the two host doubles printing their
standard output AS aifoundry1's REAL HOSTS DO (the committed bytes of 1a4bc1e3's smoke stdout.txt):
  - host-ledger prints the ledger host's line in main.cpp's two parts: the head (lines 478-492's fields, in their order, from its command
    line: ledger, prog, device, participants, shire_mask, minion_mask, harts, seed, model_s, then copy's bytes, part_bytes, passes, data,
    width; sha256's block, repeat, message_bytes, compressions_per_participant; sort's keys, reps, order) BEFORE it "opens" the card, then
    the runtime's line when it opens it, then after its launches the tail (launches, wall_s, launch_epoch_ms, records_ok, records_bad,
    units, units_expected, hart0_cycles, checked, mismatches, expect_checked, expect_mismatches, first_mismatch, status), one newline;
  - host-spp prints the runtime's line, on a line of its own, when it opens the card, and its line at the end (as its main.cpp does);
  - E191_FAKE_RUNTIME (new) says where the runtime's line falls: split (the default: INSIDE the ledger host's line, right after its head,
    as on Sun 15 Nov 2026), line (on its own line before the head), none (aifoundry3's form: no runtime line), twice (inside the line and
    once more after it), garble (an unknown text, "Warning: card busy" with its newline, inside the line instead: a line the reader must
    refuse); the line names device 1, or device 0 for a host that opened card 0 (E191_FAKE_HOST=card0);
  - the failure modes keep v1's meaning with the real hosts' stdout: crash, hang and wedge print the head and the runtime's line and no
    tail (the host died, or was stopped, after it opened the card); nojson prints the head, the runtime's line and v1's cut text; fail and
    fail-pass a complete line with a mismatch (status FAIL); short a complete line with fewer launches (status FAIL, every check good).
Every number is v1's (the frozen forecast's points: nothing here is a measurement). SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fake_card_e191 as V  # noqa: E402

SIZES = {"K": 1024, "M": 1024 ** 2, "G": 1024 ** 3}


def size(s):
    s = str(s)
    return int(float(s[:-1]) * SIZES[s[-1].upper()]) if s and s[-1].upper() in SIZES else int(float(s))


def runtime_mode():
    return os.environ.get("E191_FAKE_RUNTIME", "split")


def runtime_line(card):
    """What the runtime prints on stdout when the host opens its card (aifoundry1's), or the garble mode's unknown text."""
    m = runtime_mode()
    if m == "garble":
        return "Warning: card busy\n"
    return "" if m == "none" else f"Opening device {card}\n"


def ledger_head(argv, model_s):
    """main.cpp lines 478-492: the head, before the card opens (no newline)."""
    prog = V.arg(argv, "--prog")
    h = {"ledger": 1, "prog": prog, "device": "card", "participants": 2048, "shire_mask": "0xffffffff", "minion_mask": "0x0", "harts": 2,
         "seed": 1, "model_s": round(model_s, 4)}
    if prog == "copy":
        b = size(V.arg(argv, "--bytes", "1G"))
        h.update({"bytes": b, "part_bytes": b // 2048, "passes": int(V.arg(argv, "--passes", "1")), "data": V.arg(argv, "--data", "random"),
                  "width": int(V.arg(argv, "--width", "32"))})
    elif prog == "sha256":
        blk, rep = size(V.arg(argv, "--block", "2048")), int(V.arg(argv, "--repeat", "1"))
        h.update({"block": blk, "repeat": rep, "message_bytes": blk * rep, "compressions_per_participant": rep * (blk // 64) + 1})
    else:
        h.update({"keys": int(V.arg(argv, "--keys", "512")), "reps": int(V.arg(argv, "--reps", "1")), "order": V.arg(argv, "--order", "shuffled")})
    return json.dumps(h, separators=(",", ":"))[:-1]          # without its closing brace: the tail closes the line


def host_ledger(argv):
    if "--selftest" in argv:
        print(V.SELFTEST)
        return 0
    mode = V.host_mode()
    key = V.ledger_key(argv)
    f = V.forecast()[key]
    K = int(V.arg(argv, "--launches", 1))
    small = K == 1
    launch_s = (0.05 if small else f["seconds"]["point"]) * V.scale()
    out = sys.stdout
    rt = runtime_line("0" if mode == "card0" else "1") if mode != "noident" else ""
    if runtime_mode() == "line":
        out.write(rt)                                             # the line form: the runtime's line on a line of its own, first
    out.write(ledger_head(argv, f["seconds"]["point"]))          # the head, before the card opens (main.cpp 478-492)
    out.flush()
    node = V.open_card(mode)
    if runtime_mode() != "line":
        out.write(rt)                                             # the split form (aifoundry1's): inside the host's line
    out.flush()
    if mode in ("wedge", "hang"):
        return V.wedge(mode == "wedge")
    if mode == "crash":
        print("fake ledger host: crashed after it opened the card, before its line's tail", file=sys.stderr)
        return 134
    guard = {"copy-zeros": 1.5032, "copy-random": 1.5032, "sha256": 0.76803, "sort-sorted": 1.142784, "sort-shuffled": 1.142784}[key]
    bmode = mode if (not small and mode in ("short",)) else "ok"
    with V.InPass(not small):
        walls, spans = V.burst(K, launch_s, f["w_over_idle"], 0.3 * V.scale(), 9.5 * V.scale(), 0.0 if small else guard, bmode,
                               "smoke" if small else "pass")
    n = len(walls)
    P = 2048
    cyc = int(round(launch_s / V.scale() * 600e6))
    bad = 1 if mode == "fail" or (mode == "fail-pass" and not small) else 0
    if mode == "nojson":
        out.write('{"ledger":1,"prog":"cut\n')
        out.flush()
        return 124
    tail = {"launches": n, "wall_s": walls, "launch_epoch_ms": spans, "records_ok": P, "records_bad": 0, "units": 7, "units_expected": 7,
            "hart0_cycles": {"max": cyc, "min": cyc - 1000, "mean": cyc - 500.0, "n": 1024}, "checked": P, "mismatches": bad,
            "expect_checked": P if "--expect" in argv else 0, "expect_mismatches": 0, "first_mismatch": "participant 7" if bad else "",
            "status": "PASS" if (n == K and not bad) else "FAIL", "fake": True}
    out.write("," + json.dumps(tail, separators=(",", ":"))[1:] + "\n")      # main.cpp line 621 on: the tail and its newline
    if runtime_mode() == "twice" and rt:
        out.write(rt)
    out.flush()
    if node:
        node.close()
    return 0 if tail["status"] == "PASS" else 1


def host_spp(argv):
    """v1's sparse parity double, with the runtime's line on a line of its own when it opens the card (its line is printed at the end)."""
    real_open = V.open_card

    def open_card(mode):
        n = real_open(mode)
        if mode != "noident":
            sys.stdout.write(runtime_line("0" if mode == "card0" else "1"))
            sys.stdout.flush()
        return n
    V.open_card = open_card
    try:
        return V.host_spp(argv)
    finally:
        V.open_card = real_open


def main(argv):
    if argv and argv[0] == "host-ledger":
        return host_ledger(argv[1:])
    if argv and argv[0] == "host-spp":
        return host_spp(argv[1:])
    return V.main(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
