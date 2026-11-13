#!/usr/bin/env python3
"""The load ledger, version 2 (Q166, step 1 of the November checkpoint's plan): a load in, joules out, split by the
energy manual's ledger, with a band on every term and both footings on every answer.

It revives the joined load model of 26 Oct (tools/ettelem/load_model.py, retired 6 Nov) the way that model's
retirement note prescribes (docs/reports/data/2026-10-26-load-model/README.md.dated-note-1.md, "What would revive
it"): M10's kernel term in place of the 21 Sep flip prices, the energy catalogue's memory and mesh energies, and the
current leakage footing. It reads nothing at run time but the frozen constants file freeze_ledger_v2.py writes
(docs/reports/data/2026-11-12-q166-ledger-v2/frozen-v2.json); every constant there carries its committed source.

THE LEDGER (joules over a run of t seconds on one card at f MHz):

    J_over_idle = J_tensor + J_instr + J_awake + J_bytes + J_mesh + J_atomics      (at the run's starting die)
    J_heat      = k_leak(card, T0) * dT * t                                         (the run's own leakage rise)
    J_rest      = P_idle(card, T0) * t                                              (the card at rest)
    J_total     = J_rest + J_heat + J_over_idle

  J_tensor  = sum over tensor ops of (Z_f / R_f + D_kind / R_f) * v2          M10's kernel term: the format's zeros
              anchor per op plus M10's data-dependent price per op (D over the type's own zeros, at the loop rate R)
  J_instr   = sum over classes of busy hart-cycles * r_issue * e_class * v2  hart cycles spent issuing instructions
              (an epilogue, a second hart's generation), at the catalogue's issue rate and class price
  J_awake   = awake-but-not-issuing hart-cycles * e_awake * v2               a hart that runs and waits
  J_bytes   = sum over paths of bytes * p(path, card, data)                  p = zeros + (random - zeros) * phi(data)
              phi = w_set * rho/0.5 + (1 - w_set) * tau/0.5                  the set-bit form E101 found
  J_mesh    = bytes * hops * p_hop(data)
  v2        = (V / V_600)^2                                                  1 at 600 MHz

  rho = the data's share of set bits, tau = its share of bits that change between successive words (both 0.5 for
  random data, 0 for zeros). dT = k_rise * P_over_idle unless a measured rise is given.

Every term returns a point and a band [lo, hi] from its own sources' bars; the total band is the sum of the term
bands (a box, not a root-sum-square), so it is wide by construction.

Desk only: no card, no device. Standard library only.

SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
FROZEN_DEFAULT = os.path.join(REPO, "docs", "reports", "data", "2026-11-12-q166-ledger-v2", "frozen-v2.json")
F_REF_MHZ = 600.0


def load_frozen(path=None):
    return json.load(open(path or FROZEN_DEFAULT))


def _c(F, name):
    """A constant's value."""
    return F["constants"][name]["value"]


def _cb(F, name):
    """A constant's band [lo, hi] (the value itself when the constant has no band)."""
    c = F["constants"][name]
    b = c.get("band")
    return (b[0], b[1]) if b else (c["value"], c["value"])


def card_key(card):
    return {"aifoundry2": "a2", "aifoundry3": "a3", "aifoundry1-c1": "c1"}[card]


def phi(F, rho, tau, w=None):
    """The data's position between the zeros and random columns, by the set-bit form."""
    w = _c(F, "w_set") if w is None else w
    return w * (rho / 0.5) + (1.0 - w) * (tau / 0.5)


def phi_band(F, rho, tau):
    lo, hi = _cb(F, "w_set")
    vals = [phi(F, rho, tau, x) for x in (lo, hi)]
    return min(vals), max(vals)


# ------------------------------------------------------------------ the card at rest
def idle_w(F, card, T):
    """Board watts at rest at a die reading T: the footing law inside its band, else the exponential law outside."""
    law = F["idle_laws"][card]
    q = law["quad"]
    lo, hi = law["quad_band_c"]
    if lo <= T <= hi:
        return q["a"] * T * T + q["b"] * T + q["c"], "footing law (quadratic, inside its band)"
    e = law["exp"]
    return e["B"] + e["A80"] * math.exp((T - 80.0) / e["T_L"]), "exponential law (outside the footing band)"


def leak_slope(F, card, T):
    """dP_idle/dT at T, W per C, from the same law idle_w() reads."""
    law = F["idle_laws"][card]
    q = law["quad"]
    lo, hi = law["quad_band_c"]
    if lo <= T <= hi:
        return 2.0 * q["a"] * T + q["b"]
    e = law["exp"]
    return e["A80"] / e["T_L"] * math.exp((T - 80.0) / e["T_L"])


# ------------------------------------------------------------------ the pieces
def v2_factor(F, card, f_mhz):
    if abs(f_mhz - F_REF_MHZ) < 1e-9:
        return 1.0
    v = F["volts"][card]
    return (v[str(int(f_mhz))] / v["600"]) ** 2


def tensor_term(F, card, f_mhz, fmt, kind, ops):
    """J and band for `ops` tensor ops of one format on one kind: the zeros anchor plus M10's D, per op."""
    ck = card_key(card)
    an = F["zeros_anchor"][fmt][ck]
    kd = F["kinds"][kind][ck]
    rate = an["rate_ops_per_s"]
    v2 = v2_factor(F, card, f_mhz)
    eZ = an["Z_w"] / rate
    eD = kd["D_w"] / rate
    eZ_lo, eZ_hi = an["Z_band_w"][0] / rate, an["Z_band_w"][1] / rate
    eD_lo, eD_hi = kd["D_band_w"][0] / rate, kd["D_band_w"][1] / rate
    j = ops * (eZ + eD) * v2
    return {"j": j, "band": [ops * (eZ_lo + eD_lo) * v2, ops * (eZ_hi + eD_hi) * v2],
            "parts_j": {"zeros_anchor": ops * eZ * v2, "data_D_m10": ops * eD * v2},
            "per_op_nj": (eZ + eD) * v2 * 1e9, "kind": kind, "format": fmt, "ops": ops}


def instr_term(F, card, f_mhz, cls, hart_cycles):
    """J and band for hart-cycles spent issuing a class of instructions."""
    ck = card_key(card)
    e = F["instr_classes"][cls]["random_pj"][ck] * 1e-12
    e_lo = F["instr_classes"][cls]["band_pj"][0] * 1e-12
    e_hi = F["instr_classes"][cls]["band_pj"][1] * 1e-12
    r = _c(F, "issue_rate")
    r_lo, r_hi = _cb(F, "issue_rate")
    v2 = v2_factor(F, card, f_mhz)
    return {"j": hart_cycles * r * e * v2, "band": [hart_cycles * r_lo * e_lo * v2, hart_cycles * r_hi * e_hi * v2],
            "hart_cycles": hart_cycles, "class": cls}


def awake_term(F, card, f_mhz, hart_cycles):
    e = _c(F, "awake_pj_per_hart_cycle") * 1e-12
    lo, hi = _cb(F, "awake_pj_per_hart_cycle")
    v2 = v2_factor(F, card, f_mhz)
    return {"j": hart_cycles * e * v2, "band": [hart_cycles * lo * 1e-12 * v2, hart_cycles * hi * 1e-12 * v2],
            "hart_cycles": hart_cycles}


def bytes_term(F, card, path, nbytes, rho, tau):
    ck = card_key(card)
    p = F["mem_paths"][path]
    z = p["zeros_pj"]
    rnd = p["random_pj"][ck]
    ph = phi(F, rho, tau)
    pl, phh = phi_band(F, rho, tau)
    price = z + (rnd - z) * ph
    rel_lo, rel_hi = p["rel_band"]
    lo = (z + (rnd - z) * pl) * rel_lo
    hi = (z + (rnd - z) * phh) * rel_hi
    return {"j": nbytes * price * 1e-12, "band": [nbytes * lo * 1e-12, nbytes * hi * 1e-12],
            "pj_per_byte": price, "bytes": nbytes, "path": path, "phi": ph}


def mesh_term(F, nbytes, hops, rho, tau):
    p = F["mesh_hop"]
    ph = phi(F, rho, tau)
    pl, phh = phi_band(F, rho, tau)
    price = p["zeros_pj"] + (p["random_pj"] - p["zeros_pj"]) * ph
    lo = (p["zeros_pj"] + (p["random_pj"] - p["zeros_pj"]) * pl) * p["rel_band"][0]
    hi = (p["zeros_pj"] + (p["random_pj"] - p["zeros_pj"]) * phh) * p["rel_band"][1]
    return {"j": nbytes * hops * price * 1e-12, "band": [nbytes * hops * lo * 1e-12, nbytes * hops * hi * 1e-12],
            "pj_per_byte_hop": price}


# ------------------------------------------------------------------ the whole ledger
def predict(load, F):
    """One load in, the ledger out. `load`:
      card, f_mhz, die_start_c, seconds (the run's length), work_units (optional, with work_unit),
      tensor: [{format, kind, ops}], instr: [{class, hart_cycles}], awake_hart_cycles,
      bytes: [{path, bytes, rho, tau}], mesh: [{bytes, hops, rho, tau}],
      die_rise_c (optional: a measured mean rise; else forecast from k_rise)."""
    card, f = load["card"], load.get("f_mhz", F_REF_MHZ)
    t = load["seconds"]
    terms = {}
    for i, x in enumerate(load.get("tensor", [])):
        terms[f"tensor:{x['format']}:{x['kind']}:{i}"] = tensor_term(F, card, f, x["format"], x["kind"], x["ops"])
    for i, x in enumerate(load.get("instr", [])):
        terms[f"instr:{x['class']}:{x.get('what', i)}"] = instr_term(F, card, f, x["class"], x["hart_cycles"])
    if load.get("awake_hart_cycles"):
        terms["awake"] = awake_term(F, card, f, load["awake_hart_cycles"])
    for i, x in enumerate(load.get("bytes", [])):
        terms[f"bytes:{x['path']}:{x.get('what', i)}"] = bytes_term(F, card, x["path"], x["bytes"], x["rho"], x["tau"])
    for i, x in enumerate(load.get("mesh", [])):
        terms[f"mesh:{i}"] = mesh_term(F, x["bytes"], x["hops"], x["rho"], x["tau"])
    j_over = sum(v["j"] for v in terms.values())
    j_lo = sum(v["band"][0] for v in terms.values())
    j_hi = sum(v["band"][1] for v in terms.values())
    p_over = j_over / t
    T0 = load["die_start_c"]
    k_leak = leak_slope(F, card, T0)
    if load.get("die_rise_c") is not None:
        dT, dT_lo, dT_hi, dT_how = load["die_rise_c"], load["die_rise_c"], load["die_rise_c"], "measured, given"
    else:
        kr = _c(F, "k_rise_c_per_w")
        kr_lo, kr_hi = _cb(F, "k_rise_c_per_w")
        dT, dT_lo, dT_hi, dT_how = kr * p_over, kr_lo * j_lo / t, kr_hi * j_hi / t, "forecast, k_rise x P_over_idle"
    kb = F["leak_slope_band_rel"]
    j_heat = k_leak * dT * t
    j_heat_band = [k_leak * kb[0] * dT_lo * t, k_leak * kb[1] * dT_hi * t]
    p_rest, law = idle_w(F, card, T0)
    rb = F["idle_laws"][card]["rest_band_w"]
    j_rest = p_rest * t
    out = {
        "card": card, "f_mhz": f, "seconds": t, "die_start_c": T0,
        "terms": terms,
        "j_over_idle": j_over, "j_over_idle_band": [j_lo, j_hi],
        "w_over_idle": p_over, "w_over_idle_band": [j_lo / t, j_hi / t],
        "heat": {"k_leak_w_per_c": k_leak, "die_rise_c": dT, "die_rise_band_c": [dT_lo, dT_hi], "how": dT_how,
                 "j": j_heat, "band": j_heat_band, "w": j_heat / t},
        "rest": {"w": p_rest, "law": law, "j": j_rest, "band": [(p_rest - rb) * t, (p_rest + rb) * t]},
        "j_over_idle_with_heat": j_over + j_heat,
        "w_over_idle_with_heat": (j_over + j_heat) / t,
        "w_over_idle_with_heat_band": [(j_lo + j_heat_band[0]) / t, (j_hi + j_heat_band[1]) / t],
        "j_total": j_rest + j_heat + j_over,
        "j_total_band": [(p_rest - rb) * t + j_heat_band[0] + j_lo, (p_rest + rb) * t + j_heat_band[1] + j_hi],
    }
    n = load.get("work_units")
    if n:
        out["work_unit"] = load.get("work_unit", "unit")
        out["per_unit"] = {"j_over_idle": j_over / n, "j_over_idle_band": [j_lo / n, j_hi / n],
                           "j_over_idle_with_heat": (j_over + j_heat) / n,
                           "j_total": out["j_total"] / n,
                           "j_total_band": [out["j_total_band"][0] / n, out["j_total_band"][1] / n]}
    return out


if __name__ == "__main__":
    F = load_frozen()
    print(json.dumps({k: F[k] for k in ("model", "frozen_pst", "form")}, indent=1))
