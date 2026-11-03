#!/usr/bin/env python3
"""Read the tima_top instances out of a bench VCD (Q138(g)).

read_tima(vcd) -> (times, insts): times = sorted VCD timestamps; insts = {scope: {name: [(t, value_int), ...]}} for every
var declared in a scope ending in '.lane_tima.tima' (the 16 int8 units of the VPU), vectors as integers, bits LSB = [0].
X/Z read as 0 and are counted in 'xz'.
"""
import re, sys, collections

def read_tima(path, suffix="lane_tima.tima"):
    scope = []
    want = {}          # id -> list of (scope, name, width)
    f = open(path, "r")
    for line in f:
        s = line.strip()
        if s.startswith("$scope"):
            scope.append(s.split()[2])
        elif s.startswith("$upscope"):
            scope.pop()
        elif s.startswith("$var"):
            p = ".".join(scope)
            if p.endswith(suffix):
                parts = s.split()
                width, ident, name = int(parts[2]), parts[3], parts[4]
                want.setdefault(ident, []).append((p, name, width))
        elif s.startswith("$enddefinitions"):
            break
    insts = collections.defaultdict(dict)
    for ident, lst in want.items():
        for (p, name, w) in lst:
            insts[p][name] = []
    t = 0
    times = []
    xz = 0
    for line in f:
        if not line:
            continue
        c = line[0]
        if c == "#":
            t = int(line[1:])
            times.append(t)
        elif c in "01xzXZ":
            ident = line[1:].strip()
            if ident in want:
                v = 1 if c == "1" else 0
                if c not in "01":
                    xz += 1
                for (p, name, w) in want[ident]:
                    insts[p][name].append((t, v))
        elif c == "b":
            val, ident = line[1:].split()
            if ident in want:
                if re.search(r"[xzXZ]", val):
                    xz += 1
                    val = re.sub(r"[xzXZ]", "0", val)
                v = int(val, 2)
                for (p, name, w) in want[ident]:
                    insts[p][name].append((t, v))
    return times, dict(insts), xz

if __name__ == "__main__":
    times, insts, xz = read_tima(sys.argv[1])
    print(len(times), times[:4], times[-2:], "xz", xz)
    for p in sorted(insts):
        print(p, len(insts[p]))
    p = sorted(insts)[0]
    for name in ["clock", "f1_mul_en", "f1_in1", "f1_in2", "f1_in1_signed", "f1_in2_signed", "f3_in3", "f2_zap_opd3", "f2_tima_en", "f3_out"]:
        ch = insts[p][name]
        print(name, len(ch), ch[:6])
        par = collections.Counter((tt // 1000) % 2 for tt, _ in ch)
        print("   parity of change times (k=t/1000 mod 2):", dict(par))
