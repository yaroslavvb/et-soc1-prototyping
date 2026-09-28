#!/usr/bin/env python3
"""Recounts over the version-3 check's raw telemetry, for the DV2 review of 27-28 September 2026 (read-only, no card).

    python3 tools/claims-v3/dv2/recount_v3.py cool-busy [--card aifoundry1-c1]
    python3 tools/claims-v3/dv2/recount_v3.py over90
    python3 tools/claims-v3/dv2/recount_v3.py systemc
    python3 tools/claims-v3/dv2/recount_v3.py pass [--path raw/aifoundry2/cat/p11]

Run from the repository root; the data are docs/reports/data/2026-09-25-claims-v3/raw/<card>/**/*.jsonl*, the
three-card check's passes only: the gs/ directories (E48, gathers and scatters, 26 September 03:21-09:22 PDT) are filed
in the same tree but are a separate experiment and are left out, as tools/ettelem/analyze_dvfs.py (NOT_THE_CHECK) does,
so the counts here equal the DVFS page's (dvfs.json v3.sp_readouts). --with-gs puts them back in.

- cool-busy: one card's samples (every sample with a clock reading, as analyze_dvfs.py counts them), its clock and the
  SP's own clock min/max (sp.minion_mhz[1:3]; a statistics reset does not clear them), and the samples at a die mean
  (temp_c.minshire[0]) of 64 C or less with board power of 45 W or more and under 65 W: busy and under the 65 W TDP,
  where a live governor steps up (analyze_dvfs.py's band). Also each block's start temperature (block.json die_c_start).
- over90: every telemetry file whose die mean passed 90 C: samples, samples above 90, peak mean, peak hottest sensor,
  peak board power, clocks seen.
- systemc: samples carrying sp.system_c, the SP statistics' system temperature (avg, min, max), per card, and how many
  have a non-zero first value. It is not a per-sample reading of the PMIC: the SP reads the PMIC's temperature only when
  its statistics are initialised or reset (thermal_pwr_mgmt.c:2995-3001 at et-platform ffca4cbb4) and feeds min/max a
  literal 0 on every other pass (:663-664), so the count says nothing about the register between resets.
- pass: one telemetry file in detail (the 90-103 C catalogue pass by default).
"""
import argparse
import collections
import glob
import gzip
import json
import os

V3 = "docs/reports/data/2026-09-25-claims-v3"
NOT_THE_CHECK = {"gs"}      # as tools/ettelem/analyze_dvfs.py: E48's passes, filed beside the check's
WITH_GS = False


def rows(path):
    op = gzip.open if path.endswith(".gz") else open
    try:
        with op(path, "rt") as f:
            for line in f:
                try:
                    yield json.loads(line)
                except ValueError:
                    continue
    except (OSError, EOFError):
        return


def files(card="*"):
    out = []
    for f in sorted(glob.glob(os.path.join(V3, "raw", card, "**", "*.jsonl*"), recursive=True)):
        exp = os.path.relpath(f, os.path.join(V3, "raw")).split(os.sep)[1]
        if WITH_GS or exp not in NOT_THE_CHECK:
            out.append(f)
    return out


def cool_busy(card):
    n = 0
    mhz, spmm, by_exp, cb_mhz = (collections.Counter() for _ in range(4))
    tmax, wmax = -1, 0.0
    for f in files(card):
        exp = os.path.relpath(f, os.path.join(V3, "raw", card)).split(os.sep)[0]
        for r in rows(f):
            m = (r.get("mhz") or {}).get("minion") if isinstance(r.get("mhz"), dict) else None
            if m is None:
                continue
            n += 1
            mhz[int(m)] += 1
            sp = (r.get("sp") or {}).get("minion_mhz")
            if isinstance(sp, list) and len(sp) == 3:
                spmm[(sp[1], sp[2])] += 1
            t, bw = (r.get("temp_c") or {}).get("minshire"), r.get("board_w")
            if t and t[0] is not None:
                tmax = max(tmax, t[0])
            if bw is not None:
                wmax = max(wmax, bw)
            if t and t[0] is not None and t[0] <= 64 and bw is not None and 45 <= bw < 65:
                by_exp[exp] += 1
                cb_mhz[int(m)] += 1
    print(f"{card}: {n} samples; clock {dict(mhz)}; SP clock (min, max) {dict(spmm)}")
    print(f"  peak mean {tmax} C, peak board {wmax} W")
    print(f"  mean <= 64 C and 45 <= W < 65: {sum(by_exp.values())} samples {dict(by_exp.most_common())}, clock {dict(cb_mhz)}")
    starts = []
    for b in sorted(glob.glob(os.path.join(V3, "raw", card, "*", "p*", "block.json"))):
        if not WITH_GS and os.path.relpath(b, os.path.join(V3, "raw", card)).split(os.sep)[0] in NOT_THE_CHECK:
            continue
        try:
            d = json.load(open(b))
        except ValueError:
            continue
        if d.get("die_c_start") is not None:
            starts.append(d["die_c_start"])
    if starts:
        print(f"  block start temperatures: {min(starts)}-{max(starts)} C over {len(starts)} blocks "
              f"(median {sorted(starts)[len(starts) // 2]})")


def over90():
    total = 0
    for f in files():
        n = over = 0
        mx = hi = -1
        w = 0.0
        mhz = collections.Counter()
        for r in rows(f):
            t = r.get("temp_c", {}).get("minshire")
            if not t:
                continue
            n += 1
            over += t[0] > 90
            mx, hi, w = max(mx, t[0]), max(hi, t[2]), max(w, r.get("board_w") or 0)
            mhz[r.get("mhz", {}).get("minion")] += 1
        if over:
            total += over
            print(f"{os.path.relpath(f, V3)}: {n} samples, {over} above 90 C, peak mean {mx}, peak high {hi}, "
                  f"peak board {w} W, clock {dict(mhz)}")
    print(f"total samples above 90 C: {total}")


def systemc():
    tot, nz, vals = collections.Counter(), collections.Counter(), collections.Counter()
    for f in files():
        card = os.path.relpath(f, os.path.join(V3, "raw")).split(os.sep)[0]
        for r in rows(f):
            s = r.get("sp", {}).get("system_c")
            if s is None:
                continue
            tot[card] += 1
            nz[card] += s[0] != 0
            vals[tuple(s)] += 1
    print(f"samples with sp.system_c: {dict(tot)}, total {sum(tot.values())}")
    print(f"non-zero first value sp.system_c[0]: {dict(nz)}")
    print(f"values seen: {dict(vals.most_common(5))}")
    print("  (the SP statistics' system temperature: the PMIC is read only at a statistics reset; see the docstring)")


def one_pass(path):
    f = os.path.join(V3, path, "telemetry.jsonl.gz") if not path.endswith(".gz") else os.path.join(V3, path)
    rs = [r for r in rows(f) if r.get("temp_c", {}).get("minshire")]
    m = [r["temp_c"]["minshire"][0] for r in rs]
    top = max(m)
    first_top = next(r for r in rs if r["temp_c"]["minshire"][0] == top)
    print(f"{f}: {len(rs)} samples, mean {min(m)}-{top} C, above 90 C in {sum(x > 90 for x in m)}")
    print(f"  hottest sensor up to {max(r['temp_c']['minshire'][2] for r in rs)} C, I/O shire up to "
          f"{max(r['temp_c']['ioshire'][0] for r in rs)} C, board up to {max(r['board_w'] for r in rs)} W")
    print(f"  at the first {top} C sample: {first_top['temp_c']}, board {first_top['board_w']} W")
    print(f"  clock {dict(collections.Counter(r['mhz']['minion'] for r in rs))}; the pmic field equals the mean in "
          f"{sum(r['temp_c']['pmic'] == r['temp_c']['minshire'][0] for r in rs)} of {len(rs)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", choices=["cool-busy", "over90", "systemc", "pass"])
    ap.add_argument("--card", default="aifoundry1-c1")
    ap.add_argument("--path", default="raw/aifoundry2/cat/p11")
    ap.add_argument("--with-gs", action="store_true", help="also count the gs/ passes (E48), which are not the check's")
    a = ap.parse_args()
    global WITH_GS
    WITH_GS = a.with_gs
    {"cool-busy": lambda: cool_busy(a.card), "over90": over90, "systemc": systemc,
     "pass": lambda: one_pass(a.path)}[a.what]()


if __name__ == "__main__":
    main()
