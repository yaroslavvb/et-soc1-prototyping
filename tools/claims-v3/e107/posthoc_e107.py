#!/usr/bin/env python3
"""E107, POST HOC (written after the first pass's data, labelled, never a verdict): what the registered numbers imply, from e107.json, rails-e107.json and
scored.json only. Standard library.

    python3 tools/claims-v3/e107/posthoc_e107.py --e107 e107.json --rails rails-e107.json --scored scored.json --out posthoc.json --txt posthoc.txt

1. The price of a missing line: (T(arm) - T(c1)) / 128, the lines one shire's cold pass by column misses per op (desk/l2sim.txt, E105's), for the walk the
   L3 serves (c8s, c4s) and the walk that goes to DRAM (c16); the same per minion-op for energy, zeros and random.
2. One fresh block's first pass: (T(c16) - T(c1)) x 64 ops, us per minion, against R x T(R) - (R - 1) T(c1) on the ladder.
3. Traffic at 600 MHz: the L2-miss traffic, 128 lines of 64 B per shire per op, 32 shires; past the L3, 3 MB of A + B and 2 MB of C per block, a block
   being 64 ops of every minion at once (c16 only).
4. The vendor's binary, one launch (a desk prediction for whoever times the instrumented build): 64 ops a minion at T(c1) + 154 x the L3-served price, 154 of
   192 lines being what the desk L2 model has missing in one cold pass with the vendor's strides (80.2%), with the price from c8s and from E101's packed arm.
5. The speed half, a bound only: if no more than the FMA's 529 cycles of an fp32 op follow the clock, x1.333 of clock buys at most T / (T - 0.2204 us).
"""
import argparse
import json
import math

TYPES = ("fp32", "fp16", "int8")
RK = {"fp32": "randn", "fp16": "randn", "int8": "full"}
MISS_COLD, LINES, OPS_PER_BLOCK, VENDOR_COLD_MISS = 128, 192, 64, 154
E101_L3_PRICE_US = {"fp32": 3.578e-3, "fp16": 3.579e-3, "int8": 6.423e-3}   # predictions-e107.json ends.*.us_per_missing_line_l3


def T(items, name):
    it = items.get(name)
    return None if not it else 1024.0 / it["rate"]["mean"] * 1e6


def tci(items, name):
    it = items.get(name)
    if not it or it["rate"].get("ci95") is None:
        return None
    t = T(items, name)
    return t * it["rate"]["ci95"] / it["rate"]["mean"]


def Tarm(items, arm, ty):
    v = [T(items, n) for n in items if n.startswith(f"{arm}.{ty}.")]
    return sum(v) / len(v) if v else None


def E(items, name):
    it = items.get(name)
    return None if not it or not it.get("pj_op_S") or it["pj_op_S"].get("mean") is None else it["pj_op_S"]["mean"] / 1000.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e107", required=True)
    ap.add_argument("--rails", required=True)
    ap.add_argument("--scored", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--txt", required=True)
    a = ap.parse_args()
    items = json.load(open(a.e107))["items"]
    rails = json.load(open(a.rails))["items"]
    sc = json.load(open(a.scored))
    out, L = {"label": "POST HOC, labelled, never a verdict"}, ["E107 POST HOC (posthoc_e107.py), labelled, never a verdict. aifoundry3, 600 MHz.", ""]
    # 1
    out["price_per_missing_line"] = {}
    L.append("1. The price of a missing line (128 a cold pass by column misses per shire-op): ns of T, and nJ per minion-op of energy")
    for ty in TYPES:
        t1, t8, t4, t16 = (Tarm(items, x, ty) for x in ("c1", "c8s", "c4s", "c16"))
        row = {"l3_ns": None if None in (t1, t8) else 1000 * (t8 - t1) / MISS_COLD, "l3_ns_c4s": None if None in (t1, t4) else 1000 * (t4 - t1) / MISS_COLD,
               "dram_walk_ns": None if None in (t1, t16) else 1000 * (t16 - t1) / MISS_COLD}
        row["dram_over_l3"] = None if None in (row["l3_ns"], row["dram_walk_ns"]) else row["dram_walk_ns"] / row["l3_ns"]
        for kind in ("zeros", RK[ty]):
            e1, e8, e16 = (E(items, f"{x}.{ty}.{kind}") for x in ("c1", "c8s", "c16"))
            row[f"e_l3_nj_per_line_{kind}"] = None if None in (e1, e8) else (e8 - e1) / (MISS_COLD / 32)
            row[f"e_dram_walk_nj_per_line_{kind}"] = None if None in (e1, e16) else (e16 - e1) / (MISS_COLD / 32)
        out["price_per_missing_line"][ty] = row
        L.append(f"   {ty}: L3-served {row['l3_ns']:.2f} ns (c4s {row['l3_ns_c4s']:.2f}), the DRAM walk {row['dram_walk_ns']:.2f} ns, x{row['dram_over_l3']:.2f}; "
                 f"energy per missing line per minion-op, zeros {row['e_l3_nj_per_line_zeros']:.3f} / {row['e_dram_walk_nj_per_line_zeros']:.3f} nJ, "
                 f"random {row['e_l3_nj_per_line_' + RK[ty]]:.3f} / {row['e_dram_walk_nj_per_line_' + RK[ty]]:.3f} nJ (L3 / DRAM walk)")
    # 2
    out["first_pass"] = {}
    L.append("")
    L.append("2. One fresh block's first pass, us per minion (64 ops): (T(c16) - T(c1)) x 64 more than a warm pass; on the ladder R T(R) - (R - 1) T(c1) per op")
    for ty in TYPES:
        t1, t16 = Tarm(items, "c1", ty), Tarm(items, "c16", ty)
        fp = sc["rules"]["R3_reuse"]["per_format"].get(ty, {}).get("first_pass_us", {})
        out["first_pass"][ty] = {"extra_us_per_block_pass": (t16 - t1) * OPS_PER_BLOCK, "first_pass_T_by_R": fp}
        L.append(f"   {ty}: +{(t16 - t1) * OPS_PER_BLOCK:.1f} us a block; first-pass T by R " + ", ".join(f"R={r}: {v:.4f}" for r, v in fp.items()))
    # 3
    L.append("")
    L.append("3. Traffic at 600 MHz (fp32 T): L2-miss traffic 128 x 64 B per shire per op x 32 shires; past the L3 in c16, 3 MB + 2 MB per block of 64 x T")
    out["traffic_gbps"] = {}
    for arm in ("c8s", "c4s", "c16", "c8", "c16s"):
        t = Tarm(items, arm, "fp32")
        l2m = 128 * 64 * 32 / (t * 1e-6) / 1e9
        out["traffic_gbps"][arm] = {"l2_miss": l2m}
        L.append(f"   {arm}: L2-miss traffic {l2m:.0f} GB/s")
    t16 = Tarm(items, "c16", "fp32")
    ab, cc = 3 * 2 ** 20 / (OPS_PER_BLOCK * t16 * 1e-6) / 1e9, 2 * 2 ** 20 / (OPS_PER_BLOCK * t16 * 1e-6) / 1e9   # a block is 64 ops a minion, all minions at once
    out["traffic_gbps"]["c16"].update({"dram_ab_reads": ab, "c_stores": cc})
    L.append(f"   c16 past the L3: A + B {ab:.1f} GB/s, C's stores {cc:.1f} GB/s")
    # 4
    L.append("")
    L.append("4. The vendor's binary, one launch at 600 MHz (desk prediction): 64 x (T(c1) + 154 x price)")
    out["vendor_launch_us"] = {}
    for ty in ("fp32",):
        t1 = Tarm(items, "c1", ty)
        p8 = out["price_per_missing_line"][ty]["l3_ns"] / 1000
        lo, hi = sorted((OPS_PER_BLOCK * (t1 + VENDOR_COLD_MISS * E101_L3_PRICE_US[ty]), OPS_PER_BLOCK * (t1 + VENDOR_COLD_MISS * p8)))
        out["vendor_launch_us"][ty] = {"lo": lo, "hi": hi, "fma_bound_us": 64 * 546 / 600}
        L.append(f"   {ty}: {lo:.0f}-{hi:.0f} us (E101's packed price to c8s's), against the FMA-bound {64 * 546 / 600:.1f} us")
    # 5
    L.append("")
    L.append("5. The speed half, a bound: x1.333 of clock buys at most (fp32)")
    out["speed_half_bound_fp32"] = sc.get("speed_half_bound_fp32")
    L.append("   " + ", ".join(f"{k} x{v:.3f}" for k, v in sc.get("speed_half_bound_fp32", {}).items() if v))
    # rails per op
    L.append("")
    L.append("6. Rails over the idle just before each run, per minion-op (rails_e107.py): SRAM, NoC nJ; DDR droop mV")
    out["rails"] = {}
    for arm in ("c1", "c16r32", "c16r8", "c16r4", "c16r2", "c16", "c4s", "c8s", "c8", "c16s"):
        for kind in ("zeros", "randn"):
            r = rails.get(f"{arm}.fp32.{kind}", {})
            g = lambda k: (r.get(k) or {}).get("mean")
            out["rails"][f"{arm}.fp32.{kind}"] = {"sram_nj_op": g("sram_nj_op"), "noc_nj_op": g("noc_nj_op"), "ddr_droop_mv": g("ddr_droop_mv")}
            if g("sram_nj_op") is not None:
                L.append(f"   {arm:7s} fp32 {kind:6s} SRAM {g('sram_nj_op'):5.2f}  NoC {g('noc_nj_op'):5.2f}  DDR droop {g('ddr_droop_mv'):5.2f} mV")
    json.dump(out, open(a.out, "w"), indent=1)
    open(a.txt, "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
