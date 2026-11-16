#!/usr/bin/env python3
"""Desk test of the L1 model (l1_model.py) and the sort interpreter (ledger_interp.py), ledger v3 (Q193).

    /usr/bin/python3 -I -B tools/counter/test_l1_model.py [--out FILE]     # one line per check; exits 0 when all pass

1. Hand-made traces with known answers: a line reused hits; five lines in one set evict the least recently used; a
   dirty victim is written back and a clean one is not; a store that misses allocates (a write fill); an access across
   a line boundary touches two lines; the set is physical-address bit 6; a 512 B working set in two sets fits and a
   640 B one does not, the knee of facts-l1.json l1.knee.
2. The sort interpreter reproduces the counter's committed per-sort counts at 512 keys, both orders, mnemonic by
   mnemonic (Q166 estimates.json).
3. The 512-key sort's lines: the data alone (merge_sort's own order, no stack) give 640 fills a sort with 320 dirty
   evictions, in every participant tried; the interpreter's trace (the stack included) gives the design's 642.75 fills and
   322.25 dirty evictions a sort over its sweep (640 + 2.75 for the stack); the 16- and 32-key sorts miss nothing; SHA-256
   gives 12.375 fills and 6.25 dirty evictions a compression over its sweep (11-14); a 2 KiB copy part 67 fills and 33
   dirty evictions a pass. E201's other shapes (added before the land, Q193 fix-ledger3, for the verify's finding 5):
   the 256-key sort's data alone 288 fills and 144 dirty evictions a sort, through the interpreter 290.75 and 146.25
   (145.5 read fills, 145.25 write fills); the 64-key sorts 13.75 / 9.25 (sorted) and 14.25 / 9.75 (shuffled); a 128 KiB
   copy part 4,099 fills (2,051 read, 2,048 write) and 2,049 dirty evictions a pass. These values are the Q193 verify
   lane's own LRU cache and merge-sort trace (written from ledger.c, no code shared with l1_model.py), which matched
   l1_model.py case by case.
4. The simulator-log reader on lines in sw-sysemu's own format (count_kernel.py's test form): loads and stores to
   cacheable DRAM kept, the uncached alias, other regions, a killed instruction and the L1-bypassing classes dropped.
   (A synthetic log: the reader has NOT been run on a real simulator log; see l1_model.py.)
Desk only. Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import l1_model as L1  # noqa: E402
import ledger_interp as LI  # noqa: E402


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    res = []

    def check(name, got, want):
        ok = got == want
        res.append({"check": name, "got": got, "want": want, "pass": ok})
        print(f"{'PASS' if ok else 'FAIL'} {name}: got {got!r}" + ("" if ok else f", want {want!r}"))

    # 1. hand-made traces
    c = L1.L1()
    c.access(0x8000000000, 4, False)
    c.access(0x8000000004, 4, False)
    check("a line reused hits (1 fill for two loads in one line)", c.snap(), (1, 1, 0, 0))
    c = L1.L1()
    for k in range(5):                         # five lines of set 0 (bit 6 clear): 0x000, 0x080, 0x100, 0x180, 0x200
        c.access(0x8000000000 + 128 * k, 4, False)
    c.access(0x8000000000, 4, False)           # the first was evicted (LRU): a miss again
    check("LRU: the fifth line in a set evicts the least recently used", c.fills, 6)
    c = L1.L1()
    for k in range(4):
        c.access(0x8000000000 + 128 * k, 4, k == 0)    # the first line dirty
    c.access(0x8000000000 + 128 * 4, 4, False)        # evicts the dirty first line
    c.access(0x8000000000 + 128 * 5, 4, False)        # evicts a clean line
    check("a dirty victim is written back, a clean one is not", c.wbs, 1)
    check("a store that misses allocates its line (a write fill)", c.write_fills, 1)
    c = L1.L1()
    c.access(0x800000003C, 8, False)
    check("an access across a line boundary touches two lines", c.fills, 2)
    c = L1.L1()
    c.access(0x8000000000, 4, False)
    c.access(0x8000000040, 4, False)
    check("the set is address bit 6 (two adjacent lines in two sets)", [len(s) for s in c.sets], [1, 1])
    t512 = [(0x8000000000 + 64 * k, 4, False) for k in range(8)]
    t640 = [(0x8000000000 + 64 * k, 4, False) for k in range(10)]
    check("512 B in two sets fits: no steady-state fill", L1.steady(t512)["fills"], 0.0)
    check("640 B does not: every line refilled in the steady state (LRU over a cyclic sweep)",
          L1.steady(t640)["fills"], 10.0)
    # 2. the interpreter against the counter at 512 keys
    dis = LI.read_dis()
    chk = LI.check512(dis)
    for o in ("sorted", "shuffled"):
        check(f"the interpreter reproduces the counter's per-sort counts at 512 keys ({o})", chk[o]["differences"], {})
    # 3. lines
    n = 512
    fills_data = set()
    for p in (0, 1, 2, 3, 5, 8, 13, 21):
        keys = LI._desk().keys(1, n, p, "shuffled")
        inp = LI.SRC + p * n * 4
        w0 = LI.DST + p * n * 8
        s = L1.steady(L1.sort_data_trace(keys, w0, w0 + 4 * n, inp))
        fills_data.add((s["fills"], s["dirty_evictions"]))
    check("the 512-key sort's data alone: 640 fills and 320 dirty evictions a sort, every participant tried",
          sorted(fills_data), [(640.0, 320.0)])
    for order in ("sorted", "shuffled"):
        s = L1.sort_lines(512, order, dis=dis)
        check(f"the 512-key sort ({order}) through the interpreter: fills, dirty evictions a sort",
              (s["fills"], s["dirty_evictions"]), (642.75, 322.25))
    for nk in (16, 32):
        s = L1.sort_lines(nk, "shuffled", dis=dis)
        check(f"the {nk}-key sort misses nothing past the L1", (s["fills"], s["fills_range"]), (0.0, [0.0, 0.0]))
    # E201's other shapes (the verify lane's independent LRU and trace gave these values)
    fd = set()
    for p in (0, 5, 21):
        keys = LI._desk().keys(1, 256, p, "shuffled")
        w0 = LI.DST + p * 256 * 8
        s = L1.steady(L1.sort_data_trace(keys, w0, w0 + 4 * 256, LI.SRC + p * 256 * 4))
        fd.add((s["fills"], s["dirty_evictions"]))
    check("the 256-key sort's data alone: 288 fills and 144 dirty evictions a sort, every participant tried", sorted(fd),
          [(288.0, 144.0)])
    for order in ("sorted", "shuffled"):
        s = L1.sort_lines(256, order, dis=dis)
        check(f"the 256-key sort ({order}) through the interpreter: fills, read fills, write fills, dirty evictions a sort",
              (s["fills"], s["read_fills"], s["write_fills"], s["dirty_evictions"]), (290.75, 145.5, 145.25, 146.25))
    s64 = {o: L1.sort_lines(64, o, dis=dis) for o in ("sorted", "shuffled")}
    check("the 64-key sorts through the interpreter: (fills, dirty evictions) a sort, sorted and shuffled",
          [(s64[o]["fills"], s64[o]["dirty_evictions"]) for o in ("sorted", "shuffled")], [(13.75, 9.25), (14.25, 9.75)])
    s = L1.copy_lines(131072)
    check("a 128 KiB copy part (E201's DRAM copy): fills (read, write) and dirty evictions a pass",
          (s["fills"], s["read_fills"], s["write_fills"], s["dirty_evictions"]), (4099.0, 2051.0, 2048.0, 2049.0))
    s = L1.sha256_lines()
    check("SHA-256: fills and dirty evictions a compression (the sweep's mean) and the fills' range",
          (s["fills"], s["dirty_evictions"], s["fills_range"]), (12.375, 6.25, [11.0, 14.0]))
    s = L1.copy_lines(2048)
    check("a 2 KiB copy part: fills (read, write) and dirty evictions a pass",
          (s["fills"], s["read_fills"], s["write_fills"], s["dirty_evictions"]), (67.0, 35.0, 32.0, 33.0))
    # 4. the simulator-log reader
    def line(cyc, hart, msg):
        sh, rest = hart // 64, hart % 64
        return f"{cyc}: DEBUG EMU: [H{hart} S{sh}:N{rest // 16}:C{(rest % 16) // 2}:T{hart % 2}] {msg}\n"

    def ins(cyc, hart, pc, bits, text):
        return line(cyc, hart, f"I(U): 0x{pc:x} (0x{bits}) {text}")
    log = "".join([
        ins(1, 0, 0x8005801000, "0007a783", "lw x15,0(x15)"), line(1, 0, "\tMEM32[0x8100000000] : 0x5"),
        ins(2, 0, 0x8005801004, "00f72023", "sw x15,0(x14)"), line(2, 0, "\tMEM32[0x8200000040] = 0x5"),
        ins(3, 0, 0x8005801008, "0007a783", "lw x15,0(x15)"), line(3, 0, "\tMEM32[0xC100000000] : 0x5"),   # uncached alias
        ins(4, 0, 0x800580100c, "0007a783", "lw x15,0(x15)"), line(4, 0, "\tMEM32[0x0100000000] : 0x5"),   # ESR region
        ins(5, 0, 0x8005801010, "0007a783", "lw x15,0(x15)"), line(5, 0, "\tMEM32[0x8100000080] : 0x5"),
        line(5, 0, "\tInstruction killed and will be restarted"),
        ins(6, 0, 0x8005801010, "0007a783", "lw x15,0(x15)"), line(6, 0, "\tMEM32[0x8100000080] : 0x5"),
        ins(7, 0, 0x8005801014, "00000013", "flwg.ps f1,0(x15)"), line(7, 0, "\tMEM256[0x8100001000] : 0x0"),
        ins(8, 1, 0x8005801000, "0007a783", "ld x15,0(x15)"), line(8, 1, "\tMEM64[0x8300000000] : 0x0"),
    ])
    with tempfile.TemporaryDirectory() as td:
        pth = os.path.join(td, "sim.log")
        open(pth, "w").write(log)
        tr = L1.read_sim_log(pth)
    check("the log reader: hart 0's cacheable loads and stores, a killed access once, the rest dropped",
          tr.get(0), [(0x8100000000, 4, False), (0x8200000040, 4, True), (0x8100000080, 4, False)])
    check("the log reader: hart 1's 8 B load", tr.get(1), [(0x8300000000, 8, False)])
    fails = [r["check"] for r in res if not r["pass"]]
    print(f"L1 MODEL TEST {'PASS' if not fails else 'FAIL'}: {len(res) - len(fails)} of {len(res)}")
    if a.out:
        json.dump({"checks": res, "pass": not fails, "interpreter": sys.version.split()[0]}, open(a.out, "w"), indent=1)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
