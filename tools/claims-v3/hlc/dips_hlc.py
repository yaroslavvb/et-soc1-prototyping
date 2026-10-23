#!/usr/bin/env python3
"""E63, exploratory (not registered): the clock dips inside launches, described from the telemetry.

    python3 dips_hlc.py RED [RED ...] --out dips.json

For every launch, the 10 Hz samples from 1.5 s after its start to its end that do not read 800 MHz: when the first one
comes (seconds into the launch), how long the clock stays off 800 MHz, the board power just before and during, the die
and PMIC readings, and the sampler's own command latency (took_ms) at the onset. numpy not needed.
"""
import argparse
import json
import os
import statistics as st


def tel_rows(red):
    path = os.path.join(red, "tel.jsonl")
    rows = []
    for line in open(path):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        L = r.get("line", r)
        if isinstance(L, str):
            try:
                L = json.loads(L)
            except ValueError:
                continue
        try:
            ms = L["temp_c"]["minshire"]
            rows.append(dict(t=L["t_ms"] / 1000.0, mhz=L["mhz"]["minion"], w=float(L["board_w"]),
                             die=sum(ms) / len(ms), pmic=L["temp_c"].get("pmic"), took=L.get("took_ms"),
                             sram_mv=(L.get("die_mv") or {}).get("sram") if isinstance(L.get("die_mv"), dict) else None))
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            continue
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reds", nargs="+")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = {}
    for red in a.reds:
        rows = tel_rows(red)
        la = [json.loads(l) for l in open(os.path.join(red, "launches.jsonl"))]
        took = [r["took"] for r in rows if isinstance(r["took"], (int, float))]
        dips = []
        for L in la:
            t0, t1 = L["t_start_ms"] / 1000.0, L["t_end_ms"] / 1000.0
            s = [r for r in rows if t0 + 1.5 <= r["t"] <= t1]
            off = [r for r in s if r["mhz"] != 800]
            if not off:
                continue
            before = [r["w"] for r in s if r["t"] < off[0]["t"] - 0.1][-5:]
            during = [r["w"] for r in off if r["t"] > off[0]["t"] + 0.3]
            onset = [r["took"] for r in rows if off[0]["t"] - 0.25 <= r["t"] <= off[0]["t"] + 0.25
                     and isinstance(r["took"], (int, float))]
            dips.append(dict(n=L["n"], block=L["block"], cycle=L["cycle"], set=L["set"],
                             onset_s=round(off[0]["t"] - t0, 2), off_s=round(off[-1]["t"] - off[0]["t"] + 0.1, 2),
                             clocks=sorted({r["mhz"] for r in off}), board_before_w=round(st.mean(before), 2) if before else None,
                             board_during_w=round(st.mean(during), 2) if during else None,
                             die_c=round(off[0]["die"], 1), pmic_c=off[0]["pmic"], sampler_took_ms_at_onset=max(onset) if onset else None,
                             sram_mv_during=sorted({r["sram_mv"] for r in off if r["sram_mv"]})))
        n_launches = len(la)
        by_block = {}
        for d in dips:
            by_block.setdefault(d["block"], 0)
            by_block[d["block"]] += 1
        out[os.path.basename(os.path.normpath(red))] = dict(
            launches=n_launches, launches_with_dip=len(dips), per_block=by_block,
            sampler_took_ms_median=st.median(took) if took else None, dips=dips)
        print(f"{red}: {len(dips)} of {n_launches} launches dipped; onsets {[d['onset_s'] for d in dips]}")
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
