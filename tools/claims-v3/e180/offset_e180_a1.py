#!/usr/bin/env python3
"""E180's dated note A1 (E180.md.dated-note-A1.md section 5): E180-A's forecast against the two harts' start offset, from the
whole-minion bench (post hoc to the registration, before any E180 datum; the adversarial verifier's fault 7).

    python3 -B tools/claims-v3/e180/offset_e180_a1.py --dir tools/claims-v3/e180            # writes offset-e180-a1.json and .txt
    python3 -B tools/claims-v3/e180/offset_e180_a1.py --dir tools/claims-v3/e180 --check    # re-makes both, byte for byte

Input: bench/counts-offset-a1.jsonl, written by bench/run_offset_a1.sh on the mini (Fri 6 Nov 2026, 02:59-03:05 PST, the committed bench
re-built there to the registered binary's sha256 6e8dbab0...): for each start delay of hart 1 (7 to 32,000 cycles after hart 0), the
kinds E180-A's statistic reads (fadd.ps/zeros, fadd.ps/f_4, fadd.ps.acc/zeros, and fadd.ps.acc/f_4 at the registration's three launch
points). At the registered 50 cycles every line equals the committed counts-primary.jsonl or counts-accpts.jsonl line (bench and
coverage), and this script checks that.
Per delay, with forecast_e180.py's own per-instruction count (per_instr, NAMED: imported unchanged):
  dN_A = mean over the three launch points of N(acc f_4) - N(acc zeros), minus N(fadd.ps f_4) - N(fadd.ps zeros)
and E180-A's forecast in each arm's price on aifoundry3 (forecast-e180.json's prices and fadd.ps rate; F and A also need the all-nets
count I, read the same way). The lead of hart 0's sums at hart 1's start is estimated as 0.6208 / 8 = 0.0776 steps a cycle of delay
(one hart alone issues 0.6208 vector ops a cycle on the bench, bench/README.md; a block of eight adds each sum once). Standard library.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import statistics as st
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import forecast_e180 as fe  # noqa: E402

LEAD_PER_CYCLE = 0.6208 / 8
ARMS = ("P", "C", "E", "F", "A")


def build(d):
    rows = [json.loads(l) for l in open(os.path.join(d, "bench", "counts-offset-a1.jsonl"))]
    fc = json.load(open(os.path.join(d, "forecast-e180.json")))
    pr = fc["prices"]
    rate = fc["kinds"]["fadd.ps/f_4"]["W"]["aifoundry3"]["rate"]
    prim = {r["name"]: r for r in map(json.loads, open(os.path.join(d, "bench", "counts-primary.jsonl")))}
    accp = {(r["name"], r["tag"]): r for r in map(json.loads, open(os.path.join(d, "bench", "counts-accpts.jsonl")))}
    checks = []
    by = {}
    for r in rows:
        if "error" in r:
            raise SystemExit(f"a count line holds an error: {r['name']}")
        by.setdefault(r["delay"], []).append(r)
        if r["delay"] == 50:
            ref = accp.get((r["name"], "acc_p" + r["tag"][-1])) if r["name"] == "fadd.ps.acc/f_4" else prim.get(r["name"])
            checks.append({"name": r["name"], "tag": r["tag"], "equals_committed": ref is not None and ref["bench"] == r["bench"]
                           and ref["cov"] == r["cov"]})
    out = {"what": "E180 dated note A1: E180-A against the harts' start offset (offset_e180_a1.py)", "rate_fadd_ps": rate,
           "lead_steps_per_cycle_estimate": LEAD_PER_CYCLE, "check_delay50": checks, "delays": {}}
    for dl in sorted(by):
        rs = by[dl]
        pi = {}
        acc = []
        for r in rs:
            x = fe.per_instr(r)
            if r["name"] == "fadd.ps.acc/f_4":
                acc.append(x)
            else:
                pi[r["name"]] = x
        if len(acc) != 3 or len(pi) != 3:
            raise SystemExit(f"delay {dl}: {len(acc)} launch points and {len(pi)} plain kinds (want 3 and 3)")
        za, zp, p4 = pi["fadd.ps.acc/zeros"], pi["fadd.ps/zeros"], pi["fadd.ps/f_4"]
        nacc = st.mean(a["N"] - za["N"] for a in acc)
        iacc = st.mean(a["I"] - za["I"] for a in acc)
        dN = nacc - (p4["N"] - zp["N"])
        dI = iacc - (p4["I"] - zp["I"])
        W = {"P": pr["P@aifoundry3"]["pN_fJ"] * dN, "C": pr["C"]["pN_fJ"] * dN, "E": pr["E"]["pN_fJ"] * dN,
             "F": pr["F@aifoundry3"]["pN_fJ"] * dN + pr["F@aifoundry3"]["pI_fJ"] * dI, "A": pr["A@aifoundry3"]["pI_fJ"] * dI}
        out["delays"][str(dl)] = {"lead_steps_estimate": round(LEAD_PER_CYCLE * dl, 1),
                                  "N_acc_f4_points": [a["N"] - za["N"] for a in acc], "N_acc_f4_mean": nacc,
                                  "N_plain_f4": p4["N"] - zp["N"], "dN_A": dN, "dI_A": dI,
                                  "gaps_per_result_plain_f4": p4["gaps_per_result"], "rate_per_hart": p4["rate"],
                                  "A_forecast_W": {a: W[a] * 1e-15 * rate for a in ARMS}}
    reg = fc["kinds"]
    regA = {a: (reg["fadd.ps.acc/f_4"]["W"]["aifoundry3"][a] - reg["fadd.ps.acc/zeros"]["W"]["aifoundry3"][a]) -
            (reg["fadd.ps/f_4"]["W"]["aifoundry3"][a] - reg["fadd.ps/zeros"]["W"]["aifoundry3"][a]) for a in ARMS}
    out["registered_A_forecast_W"] = regA
    Ps = [v["A_forecast_W"]["P"] for v in out["delays"].values()]
    out["P_range_W"] = [min(Ps), max(Ps)]
    return out


def text(o):
    L = [f"E180 dated note A1: E180-A against hart 1's start delay (offset_e180_a1.py); aifoundry3, fadd.ps rate {o['rate_fadd_ps']:.4e}/s."]
    L.append("At 50 cycles every line equals the committed one: " + ("yes" if all(c["equals_committed"] for c in o["check_delay50"]) else "NO"))
    L.append("Registered E180-A forecast (50 cycles): " + ", ".join(f"{a} {v:+.4f}" for a, v in o["registered_A_forecast_W"].items()) + " W")
    L.append("delay (cycles) | lead (steps, est.) | N acc f_4 at the 3 points | N plain f_4 | dN_A | gaps/result (plain) | A: P / C / E / F / A (W)")
    for dl, v in o["delays"].items():
        f = v["A_forecast_W"]
        L.append(f"  {int(dl):6d} | {v['lead_steps_estimate']:8.1f} | " + " ".join(f"{x:7.2f}" for x in v["N_acc_f4_points"]) +
                 f" | {v['N_plain_f4']:6.2f} | {v['dN_A']:7.2f} | {v['gaps_per_result_plain_f4']:.4f} | "
                 + " / ".join(f"{f[a]:+.3f}" for a in ARMS))
    L.append(f"P's E180-A forecast over the sweep: {o['P_range_W'][0]:+.3f} to {o['P_range_W'][1]:+.3f} W")
    return "\n".join(L) + "\n"


def write(d, outdir):
    o = build(d)
    json.dump(fe.rnd(o), open(os.path.join(outdir, "offset-e180-a1.json"), "w"), indent=1, sort_keys=True)
    open(os.path.join(outdir, "offset-e180-a1.txt"), "w").write(text(o))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if not a.check:
        write(a.dir, a.dir)
        print(open(os.path.join(a.dir, "offset-e180-a1.txt")).read())
        return
    with tempfile.TemporaryDirectory() as t:
        write(a.dir, t)
        bad = [f for f in ("offset-e180-a1.json", "offset-e180-a1.txt")
               if open(os.path.join(t, f)).read() != open(os.path.join(a.dir, f)).read()]
    print("CHECK FAIL: " + ", ".join(bad) if bad else "CHECK PASS: offset-e180-a1.json and offset-e180-a1.txt byte for byte")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
