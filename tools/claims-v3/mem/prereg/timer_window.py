#!/usr/bin/env python3
"""Card evidence on the width of hpmcounter3's short window (11 cycles, low bits 0-10, as the page says; or 12,
low bits 0-11, as the RTL simulation shows). t_raw: which low-bit values were ever read, and whether each was short.
t_glitch: the in-kernel misses of the <11 correction, by the stamp's low bits and the gap to the next stamp."""
import collections, json, os, struct, sys
HERE = os.path.dirname(os.path.abspath(__file__))
D = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "data")
def u32(n):
    m = json.load(open(os.path.join(D, n + ".json")))
    return m, struct.unpack(f"<{len(m['labels'])}I", open(os.path.join(D, n + ".u32"), "rb").read())
_, r = u32("t_raw")
t0, t1 = r[0::4], r[1::4]
short = collections.defaultdict(collections.Counter)
for a, b in zip(t0, t1):
    d = (b - a) % 2**32
    # d = 10: both or neither short; 138: t0 short only; -118: t1 short only
    sa = d == 138 or (d == 10 and (a & 127) < 11)
    sb = d == 4294967178 or (d == 10 and (b & 127) < 11 and (a & 127) < 11)
    short[a & 127][sa] += 1
    short[b & 127][sb] += 1
lows = sorted(short)
out = {"low_bits_read": lows, "reads_at_11": sum(short[11].values()),
       "short_by_low_bits_0_14": {k: dict(short[k]) for k in range(15) if short[k]}}
m, r = u32("t_glitch")
s = r[0::2]
n = [v if v < 2**31 else v - 2**32 for v in r[1::2]]
tab = collections.defaultdict(collections.Counter)
for i in range(len(s) - 1):
    gap = (s[i + 1] - s[i]) % 2**32
    tab[(s[i] & 127, gap)][n[i]] += 1
out["glitch_phases"] = {f"{k[0]}|{k[1]}": dict(v) for k, v in sorted(tab.items()) if any(x != 10 for x in v)}
out["same_phase_all"] = {f"{k[0]}|{k[1]}": dict(v) for k, v in sorted(tab.items()) if k[0] in (53, 54, 55, 63, 64, 65)}

# Stamps (corrected with the <11 rule) land on every phase. A read at low bits 11 that was really short would stay
# 128 low and show as a gap of normal-128 before it and normal+128 after it. Count, per stamp low-bit value, how
# many stamps sit between two normal gaps (the build's common stamp-to-stamp gaps, each >= 1% of them; 181/221/222
# cycles in the 19 Sep build).
g = [(s[i + 1] - s[i]) % 2**32 for i in range(len(s) - 1)]
normal = {k for k, c in collections.Counter(g).items() if c >= 0.01 * len(g)}
chk = collections.defaultdict(collections.Counter)
for i in range(1, len(s) - 1):
    chk[s[i] & 127][(g[i - 1] in normal) and (g[i] in normal)] += 1
anomal = [(i, s[i] & 127, g[i - 1], g[i]) for i in range(1, len(s) - 1) if not (g[i - 1] in normal and g[i] in normal)]
out["normal_gaps"] = sorted(normal)
out["stamps_between_normal_gaps_by_low_bits_0_14"] = {k: dict(chk[k]) for k in range(15)}
out["stamps_at_11_not_clean"] = chk[11][False]
out["stamps_at_11"] = sum(chk[11].values())
out["gap_anomalies"] = anomal[:20]
out["tnop_misses"] = sum(1 for x in n if x != 10)
print(json.dumps(out, indent=1))
