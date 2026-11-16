#!/usr/bin/env python3
"""E194's desk check B, a second path for three configurations (E194.md section 15): each forecast point re-derived
through tools/ledger/ledger_v2.predict() called directly, not through forecast_e194.py's code, at aifoundry2 and 800 MHz:

  B1 sparse parity: a load built afresh from the host's --dry plan (Q166's new-dry.json) and the ledger's own pieces
     (loads_ledger_v2.sp_counts, frozen-v2.json's fitted cycle model), card 'aifoundry2', f_mhz 800, seconds model_s x
     600/800, die 55 C, with int8.pm1 carried from aifoundry3 by hand (predict() at aifoundry2 without it stops with a
     KeyError, shown);
  B2 SHA-256 and B3 copy on random bytes: the counts by mnemonic from ledger_estimate.estimate() (pinned), priced by a
     loop written here: every catalogue row a class of its own in a copy of the frozen constants (aifoundry2's mean, the
     row's lo and hi; issue cycles n / 0.37 so predict()'s instruction term is n x e x v2), the L2 bytes (SHA-256) and the
     copy's DRAM bytes as byte paths at their frozen prices (aifoundry2's DRAM-read entry; the write-back literal), the
     seconds from the catalogue's aifoundry2 issue rates at 800 MHz (SHA-256) or the byte rates (the copy); then
     predict() adds aifoundry2's idle law, its slope and the rise at 55 C.

The points must equal forecast-e194.json's at its 6 significant digits. Bands are not compared (predict() builds a band
its own way). Nothing here is measured. Standard library only.

    /usr/bin/python3 -I -B tools/claims-v3/e194/desk/rederive_e194.py     # prints REDERIVE PASS or FAIL
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import importlib.util
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E194 = os.path.dirname(HERE)
REPO = os.path.normpath(os.path.join(E194, "..", "..", ".."))
PROGS = "docs/reports/data/2026-11-12-q166-progs"
CARD, CK, F_MHZ, T0 = "aifoundry2", "a2", 800.0, 55.0
P = 2048


def mod(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(REPO, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def r6(x):
    return float(f"{x:.5e}")


def main():
    sys.path.insert(0, os.path.join(REPO, "tools", "ledger"))
    import ledger_v2 as LV  # noqa: E402
    import loads_ledger_v2 as L  # noqa: E402
    F = LV.load_frozen(os.path.join(REPO, "docs/reports/data/2026-11-12-q166-ledger-v2/frozen-v2.json"))
    fc = json.load(open(os.path.join(E194, "forecast-e194.json")))["configs"]
    res = {}
    # ---------------- B1 sparse parity
    dry = json.loads(open(os.path.join(REPO, PROGS, "runs/p2-dry/new-dry.json")).read().strip().splitlines()[-1])
    plan = dry.get("plan", dry)
    inst = dry.get("instance", {})
    n, k, m = int(inst.get("n", dry.get("n"))), int(inst.get("k", dry.get("k"))), int(inst.get("m", dry.get("m")))
    cy = F["cycle_model"]["FITTED"]
    cnt = L.sp_counts(n, k, m, 0, 1)
    S, U, rows, outs, ops = cnt["S"], plan["model_U"], cnt["row_tiles"], cnt["output_tiles"], cnt["ops"]
    gen = (cy["G_TILE"] / 2.0 + S * (cy["G_SLICE"] + cy["G_K"] / 8.0)) * (1.0 + cy["KAPPA_G"] * U)
    cov = S * 1024.0 / F["probe_rates_b_per_minion_cycle"]["scp_store"]
    h0 = ops * cy["C_OP_str"] * (1.0 + cy["KAPPA_T"] * U) + outs * (cy["D_OUT_str"] + cy["E_OUT"]) + rows * cy["H_TILE"]
    h1 = rows * gen
    t = plan["model_s"] * 600.0 / F_MHZ
    cycles_per_hart = 1024 * F_MHZ * 1e6 * t
    x = L.DATA["pm1_int8"]
    load = {"card": CARD, "f_mhz": F_MHZ, "die_start_c": T0, "seconds": t,
            "tensor": [{"format": "int8", "kind": "int8.pm1", "ops": ops}],
            "instr": [{"class": "vec_int", "hart_cycles": outs * cy["E_OUT"]},
                      {"class": "vec_int", "hart_cycles": rows * cy["H_TILE"]},
                      {"class": "vec_int", "hart_cycles": rows * max(0.0, gen - cov)}],
            "awake_hart_cycles": max(0.0, cycles_per_hart - h0) + max(0.0, cycles_per_hart - h1),
            "bytes": [{"path": "scp_load", "bytes": 2048.0 * ops, "rho": x[0], "tau": x[1]},
                      {"path": "scp_store", "bytes": 1024.0 * S * rows, "rho": x[0], "tau": x[1]},
                      {"path": "dram_load", "bytes": 32.0 * n * S * 64.0, "rho": x[0], "tau": x[1]},
                      {"path": "l2_stream", "bytes": 192.0 * S * rows, "rho": x[0], "tau": x[1]}]}
    try:
        LV.predict(load, F)
        keyerr = "no KeyError (unexpected)"
    except KeyError as e:
        keyerr = f"KeyError {e}"
    G = copy.deepcopy(F)
    G["kinds"]["int8.pm1"][CK] = dict(F["kinds"]["int8.pm1"]["a3"])          # carried by hand
    pr = LV.predict(load, G)
    res["sparse-parity"] = {"j_over_idle": pr["j_over_idle"], "j_total": pr["j_total"], "seconds": t,
                            "without_the_carry": keyerr}
    # ---------------- B2, B3: the plain programs' counts priced by a loop of rows through predict()
    le = mod("ledger_estimate_rd194", "workloads/ledger/ledger_estimate.py")
    for kk in ("sort-sorted", "sort-shuffled"):
        le.CARD[kk]["reps"] = 1800
    ea = argparse.Namespace(runs=os.path.join(REPO, PROGS, "runs"), repo=REPO,
                            dis=os.path.join(REPO, PROGS, "kernel", "ledger.dis.gz"), t0=T0, spp_dry=None, spp_slices=None,
                            spp_sites=None, spp_dis=None, out=None)
    est = le.estimate(ea)
    cat = json.load(open(os.path.join(REPO, "docs/reports/data/2026-09-23-energy-manual/catalogue.json")))

    def row(pat):
        c = cat["combined"][f"{pat}/random/h2"]
        return c["per_card"][CARD]["mean"], c["lo"], c["hi"]

    def rate(pat):
        return statistics.mean(b["ops_per_cycle_per_hart"] for b in cat["bursts"][CARD] if b["cfg"] == f"{pat}/random/h2")

    def pat_of(mn):
        return {"@taken": "beq_taken", "@not_taken": "bne_nottaken", "@jump": "jal"}.get(mn, le.ALIAS.get(mn, mn))

    for key in ("sha256", "copy-random"):
        pr_ = est["programs"][key]
        # the counts by mnemonic, as the estimator records them per participant: its fixed part (the copy's per-pass part
        # carried in at the card's passes) plus its units times its count per unit, for the card's 2,048 participants
        counts = {}
        for mn in set(pr_["fixed_per_participant"]) | set(pr_["per_unit_per_participant"]):
            counts[mn] = P * (pr_["fixed_per_participant"].get(mn, 0.0) + pr_["units_per_participant"] *
                              pr_["per_unit_per_participant"].get(mn, 0.0))
        if key.startswith("copy"):
            for mv in ("flw.ps", "fsw.ps", "ld", "sd"):    # the moves are inside the DRAM byte prices
                counts.pop(mv, None)
        G = copy.deepcopy(F)
        r_issue = LV._c(G, "issue_rate")
        instr, cyc = [], 0.0
        for mn, nn in sorted(counts.items()):
            if not nn:
                continue
            pat = pat_of(mn)
            e, lo, hi = row(pat)
            cls = "row:" + pat
            G["instr_classes"].setdefault(cls, {"random_pj": {CK: e}, "band_pj": [lo, hi]})
            instr.append({"class": cls, "hart_cycles": nn / r_issue})
            cyc += nn / rate(pat)
        ld = {"card": CARD, "f_mhz": F_MHZ, "die_start_c": T0, "instr": instr, "bytes": []}
        if key == "sha256":
            t_ = cyc / P / (F_MHZ * 1e6)
            lines = pr_["units_per_participant"] * P
            G["mem_paths"]["l2_literal"] = {"zeros_pj": 2.83, "random_pj": {CK: 2.83}, "rel_band": [1.0, 1.0]}
            ld["bytes"].append({"path": "l2_literal", "bytes": lines * 64.0, "rho": 0.5, "tau": 0.5})
        else:
            nb = float((1 << 30) * 14)
            t_ = 0.5 * (nb / 27e9 + (nb / 27e9 + nb / (LV._c(F, "dram_bandwidth_gb_s") * 1e9)))
            G["mem_paths"]["wb_literal"] = {"zeros_pj": 325.8, "random_pj": {CK: 325.8}, "rel_band": [1.0, 1.0]}
            ld["bytes"].append({"path": "dram_load", "bytes": nb, "rho": 0.5, "tau": 0.5})
            ld["bytes"].append({"path": "wb_literal", "bytes": nb, "rho": 0.5, "tau": 0.5})
        ld["seconds"] = t_
        pq = LV.predict(ld, G)
        res[key] = {"j_over_idle": pq["j_over_idle"], "j_total": pq["j_total"], "seconds": t_}
    ok = True
    print("second path through ledger_v2.predict() at aifoundry2, 800 MHz, 55 C (point values; 6 significant digits):")
    for key, v in res.items():
        f = fc[key]
        same = (r6(v["j_over_idle"]) == f["j_over_idle"] and r6(v["j_total"]) == f["j_total"]
                and r6(v["seconds"]) == f["seconds"]["point"])
        ok &= same
        print(f"  {key:14s} J over idle {v['j_over_idle']:.7f} (frozen {f['j_over_idle']}); J with the card at rest "
              f"{v['j_total']:.7f} (frozen {f['j_total']}); seconds {v['seconds']:.7f} (frozen {f['seconds']['point']}): "
              f"{'EQUAL' if same else 'DIFFERS'}")
    print(f"  sparse parity at aifoundry2 without the carry: {res['sparse-parity']['without_the_carry']}")
    print("REDERIVE " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
