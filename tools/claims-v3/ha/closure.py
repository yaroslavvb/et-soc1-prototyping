#!/usr/bin/env python3
"""E67 (Q128) closure test: do the summed per-position prices reproduce a random-data step?

    python3 tools/claims-v3/ha/closure.py --gen <make_hl.py dir> --e67 <E67 hl.json> --e65 <E65 hl.json>
        --out closure.json

The per-position price lists are measured one bit at a time. A random operand flips many positions at once. This
walks the issue order of `nrd_a` (A random, B = 1.0) and `nrd_b` (A = 1.0, B random) out of their own operand
files, counts how many flips land at each of the 32 positions, prices that histogram with E67's A-side list and
E65's B-side list, and compares the total against the step the card actually measured for those same two items on
the same passes. No model is fitted here: it is an addition and a ratio.

Pure Python by design — it reads the operand files as little-endian uint32 and re-derives the issue order of
make_hl.py:issue_streams, so it needs no numpy and can run anywhere the data is.
"""
import argparse
import json
import struct

N = 16


def read_tiles(path):
    raw = open(path, "rb").read()
    w = struct.unpack("<512I", raw)
    A = [list(w[r * N:(r + 1) * N]) for r in range(N)]
    B = [list(w[256 + r * N:256 + (r + 1) * N]) for r in range(N)]
    return A, B


def streams(A, B):
    """make_hl.py:issue_streams — for each B row k, for each A row i, two micro-ops; A is held across both."""
    a_seq, b_seq = [], []
    for k in range(N):
        for i in range(N):
            for half in (0, 1):
                a_seq.append([A[i][k]] * 8)
                b_seq.append([B[k][half * 8 + l] for l in range(8)])
    return a_seq, b_seq


def position_hist(seq):
    """Flips at each of the 32 bit positions, summed over eight lanes and the 512 micro-ops (wrapping)."""
    h = [0] * 32
    n = len(seq)
    for t in range(n):
        nxt = seq[(t + 1) % n]
        for l in range(8):
            d = seq[t][l] ^ nxt[l]
            while d:
                b = d & -d
                h[b.bit_length() - 1] += 1
                d ^= b
    return h


def price(hist, table):
    """sum_j hist[j] * J per flipped bit at j. Returns (J per multiply-add, positions with no price)."""
    tot, missing = 0.0, []
    for j, n in enumerate(hist):
        if not n:
            continue
        if j not in table:
            missing.append(j)
            continue
        tot += n * table[j]
    return tot, missing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True)
    ap.add_argument("--e67", required=True)
    ap.add_argument("--e65", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--turnon", default="grid",
                    help="post hoc: the per-item turn-on W to take out of every per-position price before "
                         "summing. 'grid' reads it from E67's own grid as minus the mean interaction excess, "
                         "'none' leaves the prices as measured, or give a number in watts.")
    a = ap.parse_args()
    C67 = json.load(open(a.e67))["cards"]["aifoundry3"]
    C65 = json.load(open(a.e65))["cards"]["aifoundry3"]
    A_PRICE = {int(k): v["J_per_alternating_bit"] for k, v in C67.get("a_bits", {}).items()}
    B_PRICE = {int(k): v["J_per_alternating_bit"] for k, v in C65.get("bits", {}).items()}
    # ---- post hoc (not a registered prediction), added after pass 750 and before the grid's data:
    # a per-position price measured against a CONSTANT-operand zero is ΔW_j = T + e_j·n_j·rate, where T is the
    # fixed cost of making the operand move at all (E60's amendment A1 called it the turn-on and warned that the
    # bit scan is "not a per-flip price"). Summing those prices over a random workload's histogram therefore
    # charges T once for every position that flips, not once for the workload. The interaction grid measures T
    # directly: if each single-flip item carries the same T, the excess (cell − A-only − B-only + base) is −T.
    # So the closure is reported twice: as measured, and with T taken out of every price and added back once.
    turnon = None
    if a.turnon == "grid":
        g = C67.get("ix") or {}
        if g.get("excess_mean_W") is not None:
            turnon = -g["excess_mean_W"]
    elif a.turnon != "none":
        turnon = float(a.turnon)
    out = {"a_price_fJ": {k: v * 1e15 for k, v in sorted(A_PRICE.items())},
           "b_price_fJ": {k: v * 1e15 for k, v in sorted(B_PRICE.items())}, "items": {},
           "turn_on_W": turnon, "turn_on_source": a.turnon}
    for name in ("nrd_a", "nrd_b"):
        it = C67["items"].get(name)
        if not it or it.get("d_p80") is None:
            out["items"][name] = {"skipped": "not measured"}
            continue
        A, B = read_tiles(f"{a.gen}/tiles/{name}.bin")
        a_seq, b_seq = streams(A, B)
        ha, hb = position_hist(a_seq), position_hist(b_seq)
        ja, missa = price(ha, A_PRICE)
        jb, missb = price(hb, B_PRICE)
        rate = it["rate"]
        pred_w = (ja + jb) * rate
        meas = it["d_p80"]
        rec = {"A_hist": ha, "B_hist": hb, "A_bits": sum(ha), "B_bits": sum(hb),
               "J_A_per_op": ja, "J_B_per_op": jb, "rate_ops_s": rate,
               "predicted_W": pred_w, "measured_W": meas, "measured_se": it.get("d_p80_se"),
               "ratio_measured_over_predicted": (meas / pred_w) if pred_w else None,
               "zero": it.get("zero"), "unpriced_positions": {"A": missa, "B": missb}}
        if turnon is not None and rate:
            # e_j = p_j − T/(n_j·rate); n_j is 2,048 on the A side and 4,096 on the B side
            mj, times = 0.0, 0.0
            for j, n in enumerate(ha):
                if n and j in A_PRICE:
                    mj += n * (A_PRICE[j] - turnon / (2048 * rate))
                    times += n / 2048
            for j, n in enumerate(hb):
                if n and j in B_PRICE:
                    mj += n * (B_PRICE[j] - turnon / (4096 * rate))
                    times += n / 4096
            pc = turnon + mj * rate            # the turn-on paid once, then the marginal flips
            rec["turn_on_counted_times_in_raw_sum"] = times
            rec["predicted_W_turnon_corrected"] = pc
            rec["ratio_measured_over_predicted_corrected"] = (meas / pc) if pc else None
        out["items"][name] = rec
    # the both-sides anchor: the kernel makes its own randn operands, so nrd_a + nrd_b is the counted stand-in
    anc = C67.get("anchors", {})
    if all(n in anc and anc[n].get("p80") is not None for n in ("anchor_randn", "anchor_zeros")):
        step = anc["anchor_randn"]["p80"] - anc["anchor_zeros"]["p80"]
        parts = [out["items"][n] for n in ("nrd_a", "nrd_b") if "predicted_W" in out["items"].get(n, {})]
        standin = sum(p["predicted_W"] for p in parts) if len(parts) == 2 else None
        out["randn_step"] = {"anchor_randn_W": anc["anchor_randn"]["p80"], "anchor_zeros_W": anc["anchor_zeros"]["p80"],
                             "step_W": step, "counted_standin_W": standin,
                             "ratio_step_over_standin": (step / standin) if standin else None,
                             "note": "anchor_randn's operands are generated by the kernel, not from a file, so its "
                                     "flip histogram is not countable; nrd_a + nrd_b is the nearest counted stimulus "
                                     "(one random side each) and is reported as a stand-in, not as the same workload."}
    json.dump(out, open(a.out, "w"), indent=1)
    for n, d in out["items"].items():
        if "predicted_W" in d:
            extra = ""
            if d.get("predicted_W_turnon_corrected") is not None:
                extra = (f"; turn-on corrected {d['predicted_W_turnon_corrected']:.3f} W, ratio "
                         f"{d['ratio_measured_over_predicted_corrected']:.3f} "
                         f"(the raw sum charges the turn-on {d['turn_on_counted_times_in_raw_sum']:.1f} times)")
            print(f"{n}: {d['A_bits']} A bits + {d['B_bits']} B bits per op; predicted {d['predicted_W']:.3f} W, "
                  f"measured {d['measured_W']:.3f} +- {d['measured_se'] or 0:.3f} W, "
                  f"measured/predicted {d['ratio_measured_over_predicted']:.3f}{extra}")
    if "randn_step" in out:
        r = out["randn_step"]
        print(f"anchor_randn - anchor_zeros = {r['step_W']:.2f} W; counted stand-in (nrd_a + nrd_b) "
              f"{r['counted_standin_W'] and round(r['counted_standin_W'], 2)} W; ratio "
              f"{r['ratio_step_over_standin'] and round(r['ratio_step_over_standin'], 3)}")


if __name__ == "__main__":
    main()
