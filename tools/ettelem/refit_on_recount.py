#!/usr/bin/env python3
"""Q126(c), second pass: the four flip energies refitted on job (b)'s toggle recount, verified.

    /usr/local/bin/python3.12 tools/ettelem/refit_on_recount.py [-o <path>]

Writes docs/reports/data/2026-10-26-load-model/refit_on_recount.json. It touches nothing the first pass
published: the frozen predictions and their scores stand as they are. A recount changes the price per
counted event and not the watts, so it is a separate pass, as the brief asks.

What it does, in order:

1.  RE-RUNS THE FIRST PASS. scores.json's `toggle_recount_refit` was computed before job (b)'s d1059a8e.
    Two of its three fits re-run here to the last float digit; the third cannot be re-run at all, because
    d1059a8e rewrote hier-factors.json and the recipe that fit used is now forbidden by that file's own
    _how_to_use. Both outcomes are recorded rather than quietly dropped.

2.  REBUILDS THE RUNGS on job (b)'s corrected recipe: the mult/rest SHARES always come from
    by_block_settled, and the rung chooses only the total (load_model.RUNG_HOW). That one change turns the
    multiplier price from -1.769 fJ (unphysical) into about +1.2 fJ.

3.  CONVERTS each fitted price to the effective capacitance one counted event switches, E = 0.5 C V^2.

4.  RE-SCORES E60's 26-item frozen bit-flip ladder under every rung's prices. E60's items are counted in
    the BENCH's currency, so each class is converted with kappa = (rung count / bench count) summed over
    the 14 patterns; the sensitivity to kappa is reported beside the number, and it is wider than the
    shift, which is the whole answer to "does the over-prediction shrink".
"""
import argparse
import datetime as dt
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import load_model as L                                     # noqa: E402
import score_load_predictions as S                         # noqa: E402

RC_P = os.path.join(L.RECOUNT_DIR, "recount.json")
HF_P = os.path.join(L.RECOUNT_DIR, "hier-factors.json")
E60_DIR = os.path.join(L.DATA, "2026-10-20-bitflip-ladder")
OUT_DEFAULT = os.path.join(L.DATA, "2026-10-26-load-model", "refit_on_recount.json")
RUNGS = ["bench", "settled", "ids", "hier", "hier_one_factor", "distinct", "distinct_one_factor",
         "hier_by_block"]
C0S = (0.0, L.STATIC["c0_w"])
PATS = list(S.MEAS14)


def fF(e_fJ):
    """The capacitance one counted event switches: E = 0.5 C V^2 for a single transition at V_REF."""
    return 2.0 * e_fJ / (L.V_REF ** 2)


def counts_by_rung():
    tog = L.load(L.D21, "toggles.json")
    out = {"bench": {p: {c: L.flips_from_toggles(tog, p)[c] for c in L.CLASSES} for p in PATS}}
    for r in RUNGS[1:]:
        rd = L.recount_reading(r)
        if rd is None or "unreadable" in rd:
            raise SystemExit(f"rung {r}: {(rd or {}).get('unreadable', 'recount.json is not here')}")
        out[r] = {p: rd["per_pattern"][p] for p in PATS}
    return out


FIRST_PASS_COMMIT = "10c911d5"          # the commit that wrote the first pass's toggle_recount_refit


def verify_the_first_pass(counts, fits, head):
    """Re-run what the first pass published, and say exactly which numbers survive.

    The published block is read from FIRST_PASS_COMMIT, not from the working tree: this script's own run
    replaces that block in scores.json, so reading the working copy would compare a thing with itself."""
    rel = "docs/reports/data/2026-10-26-load-model/scores.json"
    raw = subprocess.run(["git", "-C", L.REPO, "show", f"{FIRST_PASS_COMMIT}:{rel}"],
                         capture_output=True, text=True)
    if raw.returncode == 0:
        pub = json.loads(raw.stdout).get("toggle_recount_refit", {})
        where = f"{rel} at {FIRST_PASS_COMMIT}"
    else:                                                   # no git here: fall back to the working copy
        pub = json.load(open(os.path.join(L.REPO, rel))).get("toggle_recount_refit", {})
        where = f"{rel} in the working tree ({FIRST_PASS_COMMIT} could not be read)"
    ver = {"reran_under_commit": head, "published_block_read_from": where,
           "what": ("the first pass's toggle_recount_refit, re-run against the files as they stand now. "
                    "Job (b)'s d1059a8e landed after it was written.")}

    def same(mine, theirs):
        return (all(abs(mine["prices_fJ"][c] - theirs["prices_fJ"][c]) < 1e-12 for c in L.CLASSES)
                and abs(mine["in_sample_rms_w"] - theirs["in_sample_rms_w"]) < 1e-12
                and abs(mine["leave_one_out_rms_w"] - theirs["leave_one_out_rms_w"]) < 1e-12)

    for key, mine_rung, pub_get in (("bench_counts", "bench", lambda c0: pub["bench_counts"][c0]),
                                    ("per_net_by_block_hier", "hier_by_block",
                                     lambda c0: pub["recount_rungs"]["hier"]["fits"][c0])):
        ver[key] = {}
        for c0 in ("0.0", "-1.18"):
            try:
                theirs = pub_get(c0)
            except (KeyError, TypeError):
                ver[key][c0] = {"published": None, "note": "not in scores.json"}
                continue
            mine = fits[mine_rung][c0]
            ver[key][c0] = {"reproduces_to_the_last_digit": same(mine, theirs),
                            "published": {k: theirs[k] for k in
                                          ("prices_fJ", "in_sample_rms_w", "leave_one_out_rms_w")},
                            "rerun": {k: mine[k] for k in
                                      ("prices_fJ", "in_sample_rms_w", "leave_one_out_rms_w")}}
    r = L.recount_reading("settled_over_hf")
    hf = json.load(open(HF_P))
    ver["settled_over_hf"] = {
        "reproduces": False,
        "why": (r or {}).get("unreadable", "the rung is gone"),
        "what_it_did_before_the_guard": ("it divided by_block_settled by hier-factors.json's per-module "
                                         "factor; 12 of the 40 modules now carry a null factor, so the "
                                         "divide raised TypeError"),
        "hier_factors_now_says": hf["_how_to_use"],
        "published_numbers_that_can_no_longer_be_reproduced":
            {c0: {k: pub["recount_rungs"]["settled_over_hf"]["fits"][c0][k]
                  for k in ("prices_fJ", "in_sample_rms_w", "leave_one_out_rms_w")}
             for c0 in ("0.0", "-1.18")} if "recount_rungs" in pub else None,
        "read_instead": "the hier_one_factor rung below, which is the recipe hier-factors.json now gives"}
    return ver


def e60_rescore(counts, fits):
    """E60's frozen ladder under each rung's prices.

    pred_W for an item is exactly linear in the four flip columns -- backing the constant out of the
    published pred_W gives the same 1.146157e-06 W per fJ-weighted flip for all 26 items -- so a new price
    vector re-scores the ladder exactly, given a currency conversion for the counts."""
    pred = json.load(open(os.path.join(E60_DIR, "predictions.json")))
    hl = json.load(open(os.path.join(E60_DIR, "hl.json")))
    e_pub = dict(L.K.e_fJ)

    def score_card(card, prices, kappa):
        C = hl["cards"][card]
        rs = C.get("rtl_score")
        if not rs:
            return None
        rows = []
        for n, rec in rs["items"].items():
            z = C["items"][n]["zero"]
            fa, fz = pred["items"][n]["flips_per_op"], pred["items"][z]["flips_per_op"]
            d = {c: fa[c] - fz[c] for c in L.CLASSES}
            old = sum(e_pub[c] * d[c] for c in L.CLASSES)
            if not old:
                continue
            R = rec["pred_W"] / old
            rows.append({"item": n, "measured_W": rec["measured_W"], "pred_published_W": rec["pred_W"],
                         "pred_this_rung_W": sum(prices[c] * kappa[c] * d[c] for c in L.CLASSES) * R})
        m = [r["measured_W"] for r in rows]

        def sc(pp):
            return {"n_items": len(rows),
                    "rms_W": math.sqrt(sum((a - b) ** 2 for a, b in zip(m, pp)) / len(rows)),
                    "ratio_measured_over_pred":
                        sum(a * b for a, b in zip(m, pp)) / sum(b * b for b in pp),
                    "residuals_sharing_a_sign":
                        max(sum(1 for a, b in zip(m, pp) if a > b), sum(1 for a, b in zip(m, pp) if a < b))}
        return {"as_published": sc([r["pred_published_W"] for r in rows]),
                "under_this_rung": sc([r["pred_this_rung_W"] for r in rows]),
                "scale": rs["scale"], "items": rows}

    out = {}
    busy = [p for p in PATS if counts["bench"][p]["mult"] / L.MAC_OP > 700]
    for r in RUNGS:
        k = {c: (sum(counts[r][p][c] for p in PATS) / sum(counts["bench"][p][c] for p in PATS)
                 if sum(counts["bench"][p][c] for p in PATS) else 1.0) for c in L.CLASSES}
        band = {c: sorted(counts[r][p][c] / counts["bench"][p][c] for p in busy
                          if counts["bench"][p][c] > 0) for c in L.CLASSES}
        sens = {}
        for lab, idx in (("low", 0), ("high", -1)):
            kk = dict(k)
            for c in ("mult", "rest"):
                if band[c]:
                    kk[c] = band[c][idx]
            s = score_card("aifoundry3", fits[r]["0.0"]["prices_fJ"], kk)
            sens[lab] = {"kappa": kk, "aifoundry3": s["under_this_rung"]} if s else None
        at_c0 = score_card("aifoundry3", fits[r]["-1.18"]["prices_fJ"], k)
        out[r] = {
            "kappa_rung_over_bench": k,
            "kappa_over_the_busy_patterns": {c: ({"n": len(v), "low": v[0], "high": v[-1]} if v else None)
                                             for c, v in band.items()},
            "busy_patterns": busy,
            "sensitivity_to_kappa_aifoundry3": sens,
            "aifoundry3_with_the_c0_minus_1_18_prices": at_c0["under_this_rung"] if at_c0 else None,
            "cards": {c: v for c, v in ((card, score_card(card, fits[r]["0.0"]["prices_fJ"], k))
                                        for card in hl["cards"]) if v}}
        if r not in ("bench", "hier_one_factor"):
            # every item row is reproducible from this script; keep them only for the two rungs the
            # README quotes, so the file stays readable
            for v in out[r]["cards"].values():
                v.pop("items", None)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default=OUT_DEFAULT)
    a = ap.parse_args()
    head = subprocess.run(["git", "-C", L.REPO, "rev-parse", "--short=8", "HEAD"],
                          capture_output=True, text=True).stdout.strip() or "unknown"
    rc = json.load(open(RC_P))
    hf = json.load(open(HF_P))
    counts = counts_by_rung()
    fits = {r: {str(c0): L.refit_prices(S.MEAS14, S.IDLE21, kernel_offset=c0,
                                        **({} if r == "bench" else
                                           {"counts": {"per_pattern": counts[r], "rung": r}}))
                for c0 in C0S} for r in RUNGS}
    how = {"bench": "the bench's own coverage counts, toggles.json -- what every published fJ was fitted on"}
    how.update(L.RUNG_HOW)

    per_wire = {}
    for r in RUNGS:
        e, c = fits[r]["0.0"]["prices_fJ"], counts[r]["randn"]
        nets = c["mult"] + c["rest"]
        e_net = (e["mult"] * c["mult"] + e["rest"] * c["rest"]) / nets if nets else None
        per_wire[r] = {
            "counted_wires_per_multiply_add": nets / L.MAC_OP,
            "fJ_per_counted_wire": e_net,
            "fF_per_counted_wire": fF(e_net) if e_net is not None else None,
            "fJ_per_multiply_add_nets_only": (e["mult"] * c["mult"] + e["rest"] * c["rest"]) / L.MAC_OP,
            "fJ_per_multiply_add_all_four_classes":
                sum(e[k] * c[k] for k in L.CLASSES) / L.MAC_OP}

    # An outside divisor: Q126(e) counted unique physical nets on an open synthesised netlist of the same
    # unit (docs/reports/data/2026-10-26-open-netlist/POWER.md, commits 0678b3ea / e0945426). The fit's
    # nets-only energy divided by that count is the per-wire figure on a count nobody here chose.
    OPEN_NETLIST = {"mixed_netlist_nets_per_multiply_add": 3299.0,
                    "hierarchy_kept_nets_per_multiply_add": 3623.0,
                    "netlist_own_energy_pJ_per_multiply_add": [1.468, 1.516]}
    nets_fJ = per_wire["hier_one_factor"]["fJ_per_multiply_add_nets_only"]
    all_fJ = per_wire["hier_one_factor"]["fJ_per_multiply_add_all_four_classes"]
    cross = {
     "source": "docs/reports/data/2026-10-26-open-netlist/POWER.md (Q126(e))",
     "counts": OPEN_NETLIST,
     "this_fit_nets_only_fJ_per_multiply_add": nets_fJ,
     "this_fit_all_classes_fJ_per_multiply_add": all_fJ,
     "fJ_per_physical_wire_on_the_open_netlist_count": {
        k: nets_fJ / v for k, v in OPEN_NETLIST.items() if k.endswith("nets_per_multiply_add")},
     "fF_per_physical_wire_on_the_open_netlist_count": {
        k: fF(nets_fJ / v) for k, v in OPEN_NETLIST.items() if k.endswith("nets_per_multiply_add")},
     "board_fit_over_netlist_energy":
        [all_fJ / (OPEN_NETLIST["netlist_own_energy_pJ_per_multiply_add"][1] * 1000),
         all_fJ / (OPEN_NETLIST["netlist_own_energy_pJ_per_multiply_add"][0] * 1000)],
     "reading": ("the board-power fit puts about 3.7-3.8x the energy on one multiply-add that the "
                 "netlist's own power analysis does, which is the size of everything the board meter "
                 "sees and the lane's nets are not: the rest of the die that scales with the kernel, and "
                 "the board's own conversion. A 'per wire' number taken from board watts is an upper "
                 "bound on a wire by about that factor."),
    }

    doc = {
     "what": ("Q126(c) second pass: the four flip energies refitted on job (b)'s toggle recount, at every "
              "rung of its ladder, on the same 14 measured board powers and the same two bases as the "
              "first pass -- plus a verification of what the first pass published. NOTHING HERE TOUCHES "
              "THE FROZEN PREDICTIONS OR THEIR SCORES: a recount changes the price per counted event, not "
              "the watts."),
     "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
     "repo_commit": head,
     "written_by": "tools/ettelem/refit_on_recount.py",
     "measured": {"board_w": S.MEAS14, "idle_w": S.IDLE21,
                  "source": "docs/findings/10-data-dependent-power.md:42 (21 Sep, aifoundry2, 600 MHz)"},
     "recount_source": {"recount.json": os.path.relpath(RC_P, L.REPO),
                        "hier-factors.json": os.path.relpath(HF_P, L.REPO),
                        "hier_factors_total": hf.get("_total"),
                        "hier_factors_window_cycles": hf.get("_window_cycles")},
     "verification_of_the_first_pass": verify_the_first_pass(counts, fits, head),
     "rungs": {r: {"how": how[r],
                   "counts_per_multiply_add_randn": {c: counts[r]["randn"][c] / L.MAC_OP
                                                     for c in L.CLASSES},
                   "fits": fits[r],
                   "capacitance_at_c0_zero": {c: {"fJ": fits[r]["0.0"]["prices_fJ"][c],
                                                  "fF_per_counted_event":
                                                      fF(fits[r]["0.0"]["prices_fJ"][c])}
                                              for c in L.CLASSES},
                   "per_wire_on_randn_at_c0_zero": per_wire[r]} for r in RUNGS},
     "merge_factor_per_pattern": {
        p: {"settled_per_multiply_add": rc[p]["mean"]["nets_settled"] / L.MAC_OP,
            "hier_per_multiply_add": rc[p]["mean"]["nets_hier"] / L.MAC_OP,
            "distinct_per_multiply_add": rc[p]["mean"]["nets_distinct"] / L.MAC_OP,
            "settled_over_hier": (rc[p]["mean"]["nets_settled"] / rc[p]["mean"]["nets_hier"]
                                  if rc[p]["mean"]["nets_hier"] else None)} for p in PATS},
     "cross_check_against_the_open_netlist": cross,
     "e60_rescore": e60_rescore(counts, fits),
     "capacitance_convention": ("E = 0.5 C V^2 for one counted transition at V_REF = "
                                f"{L.V_REF} V, so C_fF = 2 E_fJ / V^2 = {fF(1.0):.3f} fF per fJ. A toggle "
                                "is one edge here, so a full 0->1->0 cycle costs C V^2 and counts twice."),
    }
    json.dump(doc, open(a.out, "w"), indent=1)
    print(f"wrote {a.out} ({os.path.getsize(a.out)} bytes)")

    print(f"\n{'rung':20s} {'ffclk':>8s} {'mult':>9s} {'rest':>8s} {'bus':>8s} {'in-rms':>7s} {'LOO':>7s} "
          f"{'fJ/wire':>8s} {'fF/wire':>8s}")
    for r in RUNGS:
        f, w = fits[r]["0.0"], per_wire[r]
        e = f["prices_fJ"]
        print(f"{r:20s} {e['ffclk']:8.4f} {e['mult']:9.4f} {e['rest']:8.4f} {e['bus']:8.3f} "
              f"{f['in_sample_rms_w']:7.4f} {f['leave_one_out_rms_w']:7.4f} "
              f"{w['fJ_per_counted_wire']:8.4f} {w['fF_per_counted_wire']:8.2f}")
    e = doc["e60_rescore"]
    a3 = e["bench"]["cards"]["aifoundry3"]["as_published"]
    print(f"\nE60 ladder, aifoundry3, {a3['n_items']} items")
    print(f"{'rung':20s} {'ratio m/p':>10s} {'rms W':>8s} {'one sign':>9s}   kappa band on the ratio")
    print(f"{'(as published)':20s} {a3['ratio_measured_over_pred']:10.4f} {a3['rms_W']:8.3f} "
          f"{a3['residuals_sharing_a_sign']:9d}")
    for r in RUNGS:
        s = e[r]["cards"]["aifoundry3"]["under_this_rung"]
        sens = e[r]["sensitivity_to_kappa_aifoundry3"]
        band = (f"   {sens['low']['aifoundry3']['ratio_measured_over_pred']:.4f} to "
                f"{sens['high']['aifoundry3']['ratio_measured_over_pred']:.4f}" if sens.get("low") else "")
        print(f"{r:20s} {s['ratio_measured_over_pred']:10.4f} {s['rms_W']:8.3f} "
              f"{s['residuals_sharing_a_sign']:9d}{band}")


if __name__ == "__main__":
    main()
