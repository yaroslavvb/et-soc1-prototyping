#!/usr/bin/env python3
"""Q129 stop 9 - 'Atoms, the floor': the arithmetic behind the README.

Everything here is either a physical constant, a number already published in this
repo (Q124/Q126/Q128, E60/E65), or a figure read out of public literature (every
one of those is listed in SOURCES below and cited in the README).  No card was
touched and no private data is used.

    python3 atoms.py            # prints the tables
    python3 atoms.py --json     # writes atoms.json

Run from anywhere; it writes atoms.json next to this file.
"""

from __future__ import annotations

import json
import math
import os
import sys

# ---------------------------------------------------------------------------
# constants (SI, CODATA 2018)
# ---------------------------------------------------------------------------
KB = 1.380649e-23          # J/K
QE = 1.602176634e-19       # C
LN2 = math.log(2.0)
HC_EV_CM = 1.239841984e-4  # eV per cm^-1

C0 = 273.15                # K at 0 C


def kt_ln2(celsius: float) -> float:
    """Landauer's floor, kT ln 2, in joules."""
    return KB * (celsius + C0) * LN2


def kt_ev(celsius: float) -> float:
    return KB * (celsius + C0) / QE


# ---------------------------------------------------------------------------
# this chip, and the open kit (all already public in this repo)
# ---------------------------------------------------------------------------
VDD = 0.517                # V, the minion rail at 600 MHz (E60/E64)
T_E65 = 58.0               # C, the die temperature E60/E65 launched at
T_TRIP = 66.0              # C, the governor's thermal trip (E64)
T_LEAK = 80.0              # C, the leakage corner the 16/20 Oct pages used
T_SPICE = 25.0             # C, ASAP7's TT corner

# Q128 section 1: one minimum ASAP7 RVT device, one fin, Lg 20 nm, gate 0 -> VDD
FIN_CGATE = 0.0335e-15     # F   (17.85 aC drawn per rise / VDD)
FIN_E_RISE = 8.94e-18      # J   C*V^2 drawn from the rail per rise
FIN_NE = 108               # electrons drawn per rise

# Q128 section 2: the placed open netlist's average nets
NET_SIG_C = 2.233e-15      # F   average toggling signal net
NET_SIG_E_RISE = 0.5969e-15   # J  C*V^2
NET_CLK_C = 7.794e-15      # F
NET_CLK_E_RISE = 2.083e-15    # J
NET_FINS = 14.5            # transistor fins an average signal net drives
NET_SIG_TOGGLES = 3623     # signal-net toggles per random fp32 MAC
NET_CLK_TOGGLES = 477      # clock-net toggles per random fp32 MAC

# Q126(d), ASAP7's liberty (asap7sc7p5t_INVBUF_RVT_TT_nldm_220122.lib, RVT TT), read in
# 2026-10-26-asap7-cell-energies.  THIS is the capacitance the 12/16/20 Oct pages used.
INVX1_PIN_LIB_C = 0.619928e-15     # F   cells.INVx1.inputs.A.cap_fF
INVXP33_PIN_LIB_C = 0.275723e-15   # F   cells.INVxp33.inputs.A.cap_fF
INVX1_LEAK_PW = 51.1588            # pW  at 0.7 V / 25 C
INVXP33_LEAK_PW = 17.0562          # pW  -- exactly 1/3 of INVx1's

# ASAP7's own LVS netlist, asap7sc7p5t_28/CDL/LVS/asap7sc7p5t_28_R.cdl:
#   .SUBCKT INVx1_ASAP7_75t_R    nmos_rvt nfin=3 + pmos_rvt nfin=3  -> 6 fins
#   .SUBCKT INVxp33_ASAP7_75t_R  nfin=1 + nfin=1                    -> 2 fins
# So INVx1 is a 3x cell and INVxp33 is the library's minimum inverter.
INVX1_NFIN = 6
INVXP33_NFIN = 2

# Q128 section 1, the same gate measured at the pin of a working cell.  INVx1's A, BUFx2's A
# and DFFHQx4's CLK all read exactly this in both hold states: they drive a plain inverter
# stage whose output always moves, so they carry the full Miller charge.
INV_PIN_Q_PER_FIN = 24.31e-18      # C per fin per rise
FINS_PER_DRIVEN_PIN = 6.086780909774913   # mix-weighted over the 15 types this unit drives
SCHEMATIC_OVER_LIBERTY_PIN = 0.3700221490051509   # mix-weighted; range 0.24-0.46

# The 20 Oct plan's "25,000x" rung.  Its C is NOT a guess and not back-solved: the plan states
# 0.62 fF in line (section 3.1 item 1 and section 6 of its table), the 12 Oct plan names its
# provenance ("INVx1 in ASAP7, a predictive 7 nm kit, typical corner"), and 05-claims.md
# records it as settled (S, Q126(d)).  83 aJ and 2,000 e- are its two-figure roundings of it.
PLAN_INV_C = 0.62e-15      # F   as the plan writes it
PLAN_INV_E_EDGE = 83e-18   # J   the plan's rounded 1/2 C V^2
PLAN_INV_NE = 2000         # electrons, the plan's rounded C V / e

# measured, on the card
E60_FLIP_BOARD = 116.7e-15     # J  one flipped fp32 MAC input bit, a = 1.0, board
E65_FLOWM_BOARD = 745e-15      # J  E65's flow-M flip, board
MAC_BOARD = 5.783e-12          # J  one random fp32 MAC over idle, board (E38)
MAC_LEDGER = 1.946e-12         # J  the bottom-up open ledger (Q128)
RAIL_SHARE = 0.75              # minion rail / board (E60); registered range below
RAIL_SHARE_LO = 0.70           # the spread across runs (CONTEXT section 2; data.json rail/*)
RAIL_SHARE_HI = 0.89

# Q129(a), 2026-10-27: detailed routing closed and the extraction puts the global-route
# Steiner between-cell wire capacitance 17-20% ABOVE it (14,427 fF against 12,006 fF on
# `mixed` at Miller k = 1), so Q128's wire half is not a floor.  Carried here as a declared
# sensitivity, NOT re-baselined: Q128's published ledger is still 2.233 fF.
STEINER_OVER_EXTRACTED = 14427.4 / 12006.0

# ASAP7 geometry, Clark et al. 2016 + this repo's SPICE decks
FIN_W = 6.5e-9             # m   fin width
FIN_H = 32e-9              # m   fin height
LGATE = 20e-9              # m   gate length used by this repo's decks
FIN_PITCH = 27e-9          # m
CPP = 54e-9                # m   contacted poly pitch
M1_W = 18e-9               # m   ASAP7 tech LEF, M1/M2/M3 min width
M1_PITCH = 36e-9           # m

# ASAP7 device check in this repo (2026-10-26-asap7-one-switch)
IDSAT_NFIN = 35.87e-6      # A   per fin, RVT NMOS, TT 25 C, SPICE

# ORFS asap7 setRC.tcl.  The file's numbers are in the liberty's units, kohm/um and fF/um, so
# `-resistance 2.65684E-02` is 2.65684e-2 kohm/um = 26.5684 ohm/um.
#   set_wire_rc -signal : 2.65684E-02 / 1.65790E-01   <- the AVERAGE signal wire, what the
#                                                        estimator hands every between-cell net
#   set_layer_rc M1     : 7.04175E-02 / 1e-10         <- the tightest layer in the stack, but
#                                                        ORFS gives it ~zero capacitance, i.e.
#                                                        the flow does not route signals on it
#   set_layer_rc M2     : 2.97127E-02 / 1.74942E-01   <- the tightest layer that does carry them
#   set_layer_rc M8     : 8.44765E-03 / 1.03962E-01
R_SIG_PER_UM = 26.5684     # ohm/um, average signal wire
C_SIG_PER_UM = 0.165790e-15  # F/um
R_M1_PER_UM = 70.4175      # ohm/um, M1 (tightest layer; not a signal-routing layer here)
R_M2_PER_UM = 29.7127      # ohm/um, M2 (tightest signal-routing layer)
C_M2_PER_UM = 0.174942e-15   # F/um
R_M8_PER_UM = 8.44765      # ohm/um

# ---------------------------------------------------------------------------
# silicon
# ---------------------------------------------------------------------------
SI_A = 0.5431020511e-9     # m   lattice constant
SI_ATOMS_CELL = 8
SI_N = SI_ATOMS_CELL / SI_A**3          # atoms / m^3
SI_RHO = 2329.0            # kg/m^3
SI_CP = 705.0              # J/(kg K) at 300 K
SI_CV = SI_RHO * SI_CP     # J/(m^3 K)
SI_K_300 = 148.0           # W/(m K), bulk, 300 K  (Glassbrenner & Slack 1964)
SI_K_FIN = 25.0            # W/(m K), narrow fin   (Yoo 2016: 0.25 W/(K cm))
SI_K_SD = 62.0             # W/(m K), S/D region   (Yoo 2016: 0.62 W/(K cm))
SI_K_BULK_YOO = 150.0      # W/(m K)               (Yoo 2016: 1.5 W/(K cm))

SI_RAMAN_CM = 520.7        # cm^-1, the zone-centre optical mode
E_OPT = SI_RAMAN_CM * HC_EV_CM          # eV
V_OPT = 1000.0             # m/s  optical phonon group velocity  (Pop 2006)
V_AC_TA = 5000.0           # m/s  transverse acoustic            (Pop 2006)
V_AC_LA = 9000.0           # m/s  longitudinal acoustic          (Pop 2006)

TAU_OPT = 2e-12            # s    zone-centre optical lifetime, 300 K (Cahill 2009)
TAU_HEAT = 30e-12          # s    dominant heat-carrying phonons        (Cahill 2009)
MFP_HEAT = 300e-9          # m    their mean free path                  (Cahill 2009)
MFP_E_LO = 5e-9            # m    electron inelastic MFP, high field    (Pop 2006)
MFP_E_HI = 10e-9
TAU_EPH_LO = 0.05e-12      # s    electron-phonon scattering time       (Pop 2006)
TAU_EPH_HI = 0.10e-12

# low-k and copper
LOWK_K_DENSE = 0.7         # W/(m K)  dense SiOC:H        (Alam 2014)
LOWK_K_POROUS = 0.1        # W/(m K)  30% porosity        (Alam 2014)
# 🛑 ESTIMATE, not a cited measurement, and the only one in this file: a nominal organosilicate
# density of ~1,300 kg/m^3 times a nominal ~1,000 J/(kg K).  It sets the dense-low-k alpha and
# so the ladder's 17 us row by itself.  +/-30% in rho.c moves that row +/-30% and changes no
# conclusion (it stays between the 1 ns fin pole and the 0.25 ms die).  The README's open issues
# say so, and the ladder row is marked as an estimate.
LOWK_RHO_C = 1.3e6         # J/(m^3 K)  ESTIMATE
CU_MFP = 39.9e-9           # m    electron MFP, 300 K     (Gall 2016)
CU_RHO = 1.70e-8           # ohm m
LORENZ = 2.44e-8           # W ohm / K^2

# the fin's self-heating, from published 7 nm-class work
RTH_YOO_300 = 1.05e3       # K/W   total, 300 K   (Yoo 2016: 1.05 K/mW)
RTH_YOO_350 = 1.10e3       # K/W   total, 350 K
RTH_YOO_DRAIN = 1.96e3     # K/W   drain node
RTH_YOO_SUB = 1.18e3       # K/W   substrate node

EDGE_RISE = 23e-12         # s   this design's rising edge (Q128 section 1)
EDGE_FALL = 17e-12         # s


def fmt(x, sig=4):
    if x == 0:
        return "0"
    return f"{x:.{sig}g}"


out: dict = {}

# ---------------------------------------------------------------------------
# 1. the floor, at the four temperatures the pages use
# ---------------------------------------------------------------------------
floors = {}
for t in (T_SPICE, T_E65, T_TRIP, T_LEAK):
    floors[t] = {
        "kT_ln2_J": kt_ln2(t),
        "kT_eV": kt_ev(t),
        "eVDD_over_kT": VDD / kt_ev(t),
        "one_electron_x_floor": QE * VDD / kt_ln2(t),
    }
out["floors"] = floors

# ---------------------------------------------------------------------------
# 2. the 25,000x: reproduce it, source its C, and say what it does and does not price
# ---------------------------------------------------------------------------
# the plan's own factorisation: 1/2 C V^2 / (kT ln2) = (CV/e)(eV/kT)/(2 ln2)
plan = {
    "quoted": 24500,
    "inputs": {"electrons": PLAN_INV_NE, "eVDD_over_kT_80C": VDD / kt_ev(T_LEAK),
               "divisor_2ln2": 2 * LN2},
    "reproduced": PLAN_INV_NE * (VDD / kt_ev(T_LEAK)) / (2 * LN2),
    "direct_ratio": PLAN_INV_E_EDGE / kt_ln2(T_LEAK),
    # --- where its C comes from.  Corrected Tue 27 Oct 2026 after review: the first version of
    # this file back-solved C from the plan's two rounded figures and called the result
    # unsourced.  It is sourced.  The plan STATES 0.62 fF, which is ASAP7's INVx1 liberty
    # input pin, 0.619928 fF (Q126(d)), recorded settled in docs/findings/05-claims.md.
    "C_as_the_plan_states_it_F": PLAN_INV_C,
    "C_liberty_INVx1_pin_F": INVX1_PIN_LIB_C,
    "C_stated_over_liberty": PLAN_INV_C / INVX1_PIN_LIB_C,
    "from_the_liberty_value": {
        "E_edge_J": 0.5 * INVX1_PIN_LIB_C * VDD**2,
        "electrons": INVX1_PIN_LIB_C * VDD / QE,
        "x_floor_80C": (0.5 * INVX1_PIN_LIB_C * VDD**2) / kt_ln2(T_LEAK),
        "x_floor_58C": (0.5 * INVX1_PIN_LIB_C * VDD**2) / kt_ln2(T_E65),
    },
    # the 24,509-vs-24,559 gap is the rounding of 82.85 -> 83 aJ, nothing else
    "rounding": {
        "exact_E_edge_from_liberty_aJ": 0.5 * INVX1_PIN_LIB_C * VDD**2 * 1e18,
        "plan_rounds_to_aJ": PLAN_INV_E_EDGE * 1e18,
        "exact_electrons": INVX1_PIN_LIB_C * VDD / QE,
        "plan_rounds_to_electrons": PLAN_INV_NE,
        "route_via_electrons": PLAN_INV_NE * (VDD / kt_ev(T_LEAK)) / (2 * LN2),
        "route_via_83aJ": PLAN_INV_E_EDGE / kt_ln2(T_LEAK),
        "both_are_the_same_number": "the 0.2% between them is 83/82.85, a two-figure rounding",
    },
    # 05-claims.md already corrected this rung on 26 Oct 2026 and settled it at the 58 C floor
    "repo_settled_reading": {
        "where": "docs/findings/05-claims.md, 'What one transistor switching costs on this "
                 "chip' -- Corrected 26 Oct 2026",
        "reads": "83 aJ, about 2,000 electrons, some 26,000x kT ln 2 = 3.17 zJ at 58 C",
        "x_floor_58C_rederived": (0.5 * INVX1_PIN_LIB_C * VDD**2) / kt_ln2(T_E65),
        "delta_against_the_plan": "the same energy; the plan divides by the 80 C floor and "
                                  "05-claims.md by the 58 C one (E60/E65's launch temperature). "
                                  "24,515 against 26,143 -- a 6.6% floor choice, not a physics "
                                  "disagreement",
    },
    # what the rung does and does not price.  The three real caveats, none of them 'unsourced'.
    "what_it_prices": {
        "INVx1_is_not_the_minimum_inverter": {
            "INVx1_nfin": INVX1_NFIN, "INVxp33_nfin": INVXP33_NFIN,
            "leakage_ratio": INVX1_LEAK_PW / INVXP33_LEAK_PW,
            "liberty_pin_ratio": INVX1_PIN_LIB_C / INVXP33_PIN_LIB_C,
            "note": "ASAP7's LVS netlist gives INVx1 nfin=3 on each device and INVxp33 nfin=1; "
                    "the leakage ratio is exactly 3.00.  The plan's words 'a minimum inverter' "
                    "name a 3x cell",
        },
        "the_liberty_pin_carries_the_cell's_own_wire": {
            "schematic_over_liberty_mix_weighted": SCHEMATIC_OVER_LIBERTY_PIN,
            "INVx1_schematic_pin_F": INVX1_NFIN * INV_PIN_Q_PER_FIN / VDD,
            "INVx1_schematic_over_liberty": (INVX1_NFIN * INV_PIN_Q_PER_FIN / VDD)
                                            / INVX1_PIN_LIB_C,
            "INVx1_bare_static_gate_F": INVX1_NFIN * FIN_CGATE,
            "note": "ASAP7's liberty was characterised on the parasitic-extracted netlist, so "
                    "the pin capacitance includes the cell's own layout interconnect.  Q128's "
                    "SPICE on the LVS (schematic) netlist reads 0.370 of it, mix-weighted",
        },
        "it_is_a_predictive_kit_at_another_voltage": "05-claims.md's own caveat: ASAP7 is a "
            "predictive 7 nm kit characterised at 0.7 V, not a measurement of this chip",
    },
    # the sourced comparisons, in place of the withdrawn 'unmeasured / 9.3x a pin' set
    "liberty_pin_vs": {
        "one_minimum_fin_bare_gate": INVX1_PIN_LIB_C / FIN_CGATE,
        "INVx1_six_fins_of_bare_gate": INVX1_PIN_LIB_C / (INVX1_NFIN * FIN_CGATE),
        "INVx1_same_pin_in_SPICE": INVX1_PIN_LIB_C / (INVX1_NFIN * INV_PIN_Q_PER_FIN / VDD),
        "INVxp33_liberty_pin": INVX1_PIN_LIB_C / INVXP33_PIN_LIB_C,
        "the_average_signal_net": INVX1_PIN_LIB_C / NET_SIG_C,
    },
}
out["plan_25000x"] = plan

# ---------------------------------------------------------------------------
# 3. one table that reconciles every ratio the pages print
# ---------------------------------------------------------------------------
def ratio_row(name, energy_J, convention, floor_C, electrons=None, cap_F=None):
    """convention: 'rise' = C V^2 drawn; 'edge' = 1/2 C V^2 of heat."""
    f = kt_ln2(floor_C)
    row = {
        "event": name,
        "energy_J": energy_J,
        "convention": convention,
        "floor_C": floor_C,
        "floor_J": f,
        "x_floor": energy_J / f,
    }
    if electrons is not None:
        row["electrons"] = electrons
        row["factorisation"] = {
            "electrons": electrons,
            "one_electron_x_floor": QE * VDD / f,
            "convention_factor": 1.0 if convention == "rise" else 0.5,
            "product": electrons * (QE * VDD / f) * (1.0 if convention == "rise" else 0.5),
        }
    if cap_F is not None:
        row["C_F"] = cap_F
    return row


rows = [
    ratio_row("one electron across the 0.517 V rail", QE * VDD, "rise", T_TRIP, 1),
    ratio_row("one minimum device's gate (Q128 prints 2,755x)",
              FIN_E_RISE, "rise", T_TRIP, FIN_NE, FIN_CGATE),
    ratio_row("the same gate, heat per edge (the flip page prints 1,410x)",
              FIN_E_RISE / 2, "edge", T_E65, FIN_NE, FIN_CGATE),
    # INVxp33 (nfin=1+1) is the library's MINIMUM inverter.  This row is its two fins of bare
    # static gate capacitance -- NOT an INVx1 pin, which the first version of this file called
    # it.  Corrected Tue 27 Oct 2026 after review.
    ratio_row("INVxp33 (the library's minimum inverter), its 2 fins of bare gate, heat per edge",
              INVXP33_NFIN * FIN_E_RISE / 2, "edge", T_LEAK,
              INVXP33_NFIN * FIN_NE, INVXP33_NFIN * FIN_CGATE),
    # INVx1's own input pin on the three bases the repo has for it, all per edge at 80 C
    ratio_row("INVx1's input pin, its 6 fins of bare gate (6 x 0.0335 fF)",
              0.5 * (INVX1_NFIN * FIN_CGATE) * VDD**2, "edge", T_LEAK,
              INVX1_NFIN * FIN_NE, INVX1_NFIN * FIN_CGATE),
    ratio_row("INVx1's input pin, measured in SPICE on the schematic netlist (6 x 24.31 aC)",
              0.5 * (INVX1_NFIN * INV_PIN_Q_PER_FIN / VDD) * VDD**2, "edge", T_LEAK,
              int(round(INVX1_NFIN * INV_PIN_Q_PER_FIN / QE)),
              INVX1_NFIN * INV_PIN_Q_PER_FIN / VDD),
    ratio_row("INVx1's input pin, ASAP7's liberty (0.620 fF) = THE PLAN'S ROW, heat per edge",
              0.5 * INVX1_PIN_LIB_C * VDD**2, "edge", T_LEAK,
              int(round(INVX1_PIN_LIB_C * VDD / QE)), INVX1_PIN_LIB_C),
    ratio_row("the same, at the 58 C floor = 05-claims.md's settled reading",
              0.5 * INVX1_PIN_LIB_C * VDD**2, "edge", T_E65,
              int(round(INVX1_PIN_LIB_C * VDD / QE)), INVX1_PIN_LIB_C),
    ratio_row("an INVx1 toggling this design's average signal net",
              NET_SIG_E_RISE / 2, "edge", T_LEAK, int(round(NET_SIG_E_RISE / (QE * VDD))),
              NET_SIG_C),
    ratio_row("one rise of that net", NET_SIG_E_RISE, "rise", T_TRIP,
              int(round(NET_SIG_E_RISE / (QE * VDD))), NET_SIG_C),
    ratio_row("one rise of an average clock net", NET_CLK_E_RISE, "rise", T_TRIP,
              int(round(NET_CLK_E_RISE / (QE * VDD))), NET_CLK_C),
    ratio_row("one flipped MAC input bit, a = 1.0, board (E60)",
              E60_FLIP_BOARD, "event", T_TRIP),
    ratio_row("E65's flow-M flip, board", E65_FLOWM_BOARD, "event", T_TRIP),
    ratio_row("one random fp32 MAC, bottom-up (Q128)", MAC_LEDGER, "event", T_TRIP),
    ratio_row("one random fp32 MAC, board (E38)", MAC_BOARD, "event", T_TRIP),
]
out["ratio_table"] = rows

# the three floors applied to the one event, so the spread is visible
one_event = {}
for t in (T_SPICE, T_E65, T_TRIP, T_LEAK):
    one_event[t] = {
        "gate_rise_x": FIN_E_RISE / kt_ln2(t),
        "gate_edge_x": (FIN_E_RISE / 2) / kt_ln2(t),
        "net_edge_x": (NET_SIG_E_RISE / 2) / kt_ln2(t),
    }
out["same_event_four_floors"] = one_event

# ---------------------------------------------------------------------------
# 4. phonons: how many, of what, and when
# ---------------------------------------------------------------------------
e_opt_J = E_OPT * QE
ph = {
    "optical_mode_cm1": SI_RAMAN_CM,
    "optical_mode_eV": E_OPT,
    "optical_mode_J": e_opt_J,
    "optical_mode_THz": SI_RAMAN_CM * 2.99792458e10 / 1e12,
    "phonons_per_electron_full_rail": VDD / E_OPT,
    "phonons_per_electron_per_edge": (VDD / 2) / E_OPT,
    "per_event": {},
}
for nm, en in (("one fin's gate, per edge", FIN_E_RISE / 2),
               ("average signal net, per edge", NET_SIG_E_RISE / 2),
               ("average clock net, per edge", NET_CLK_E_RISE / 2),
               ("one flipped MAC input bit, rail share of E60", E60_FLIP_BOARD * RAIL_SHARE),
               ("one random fp32 MAC, rail share of E38", MAC_BOARD * RAIL_SHARE)):
    ph["per_event"][nm] = {"energy_J": en, "optical_phonons": en / e_opt_J}
# Pop 2006's generation split
ph["generation_split_bulk_Si_high_field"] = {"LO": "just over 1/2", "LA": "~1/3", "TO": "~1/10"}
ph["ballistic_in_2ps"] = {"optical_nm": V_OPT * TAU_OPT * 1e9,
                          "TA_nm": V_AC_TA * TAU_OPT * 1e9,
                          "LA_nm": V_AC_LA * TAU_OPT * 1e9}
out["phonons"] = ph

# ---------------------------------------------------------------------------
# 5. the fin: atoms, electrons, and what one flip would do to it
# ---------------------------------------------------------------------------
vol_chan = FIN_W * FIN_H * LGATE                   # the fin segment under one gate
area_chan = (2 * FIN_H + FIN_W) * LGATE            # the inverted surface, 3 sides
vol_inv = area_chan * 1.5e-9                       # a 1.5 nm inversion shell
vol_block = FIN_PITCH * CPP * FIN_H                # one fin pitch x one gate pitch
vol_drain10 = (10e-9) ** 3                         # Pop's 5-10 nm drain hot spot

fin = {
    "Si_atoms_per_m3": SI_N,
    "Si_atoms_per_cm3": SI_N / 1e6,
    "volume_channel_m3": vol_chan,
    "volume_channel_nm3": vol_chan * 1e27,
    "atoms_channel": vol_chan * SI_N,
    "atoms_inversion_shell": vol_inv * SI_N,
    "atoms_block": vol_block * SI_N,
    "atoms_drain_10nm_cube": vol_drain10 * SI_N,
    "electrons_on_gate_per_rise": FIN_NE,
    "atoms_per_electron_channel": vol_chan * SI_N / FIN_NE,
    "dopants_at_1e17_per_cm3": 1e17 * vol_chan * 1e6,
    "dopants_at_1e18_per_cm3": 1e18 * vol_chan * 1e6,
    "C_th_channel_J_per_K": vol_chan * SI_CV,
    "C_th_block_J_per_K": vol_block * SI_CV,
    "C_th_drain10_J_per_K": vol_drain10 * SI_CV,
}
# "if it landed here and stayed": an upper bound on the transient
fin["dT_if_deposited"] = {}
for nm, en in (("one fin's gate, per edge", FIN_E_RISE / 2),
               ("average signal net, per edge", NET_SIG_E_RISE / 2)):
    fin["dT_if_deposited"][nm] = {
        "channel_K": en / fin["C_th_channel_J_per_K"],
        "channel_per_fin_if_6_fin_driver_K": en / fin["C_th_channel_J_per_K"] / 6.0,
        "block_K": en / fin["C_th_block_J_per_K"],
        "drain_10nm_cube_K": en / fin["C_th_drain10_J_per_K"],
        "energy_per_channel_atom_meV": en / fin["atoms_channel"] / QE * 1e3,
        "energy_per_channel_atom_over_kT66": (en / fin["atoms_channel"]) / (KB * (T_TRIP + C0)),
    }
# what volume the lumped Rth.Cth model actually describes, if tau ~ 1 ns
fin["lumped_model_volume"] = {
    "assumed_tau_s": 1e-9,
    "C_th_implied_J_per_K": 1e-9 / RTH_YOO_300,
    "volume_m3": (1e-9 / RTH_YOO_300) / SI_CV,
    "cube_side_nm": (((1e-9 / RTH_YOO_300) / SI_CV) ** (1 / 3)) * 1e9,
}
out["fin"] = fin

# ---------------------------------------------------------------------------
# 6. self-heating: resistance, and why the edge never sees it
# ---------------------------------------------------------------------------
p_edge = (NET_SIG_E_RISE / 2) / EDGE_RISE          # W, mean power during one edge
sh = {
    "Rth_K_per_W": {"total_300K": RTH_YOO_300, "total_350K": RTH_YOO_350,
                    "drain_node": RTH_YOO_DRAIN, "substrate_node": RTH_YOO_SUB},
    "edge_rise_s": EDGE_RISE,
    "mean_power_during_one_edge_W": p_edge,
    "quasi_steady_dT_if_Rth_applied_K": p_edge * RTH_YOO_300,
    "one_fin_at_Idsat": {
        "power_W": IDSAT_NFIN * VDD,
        "dT_K": IDSAT_NFIN * VDD * RTH_YOO_300,
    },
    "a_net_toggling_at_10pc_800MHz": {
        "power_W": 0.1 * 800e6 * NET_SIG_E_RISE,
        "dT_K": 0.1 * 800e6 * NET_SIG_E_RISE * RTH_YOO_300,
    },
}
out["self_heating"] = sh

# ---------------------------------------------------------------------------
# 7. the ladder: ps -> ns -> us -> ms, by diffusion where diffusion applies
# ---------------------------------------------------------------------------
alpha_si = SI_K_300 / SI_CV
alpha_fin = SI_K_FIN / SI_CV
alpha_lowk = LOWK_K_DENSE / LOWK_RHO_C
ladder = {
    "alpha_Si_m2_per_s": alpha_si,
    "alpha_narrow_fin_m2_per_s": alpha_fin,
    "alpha_lowk_dense_m2_per_s": alpha_lowk,
    "steps": [],
}


def step(what, length_m, alpha, note):
    t = length_m ** 2 / alpha
    ladder["steps"].append({"what": what, "length_m": length_m,
                            "alpha_m2_per_s": alpha, "time_s": t, "note": note})


step("across the fin (6.5 nm)", FIN_W, alpha_fin, "shorter than one phonon MFP: not diffusion")
step("along the gate (20 nm)", LGATE, alpha_fin, "shorter than one phonon MFP: not diffusion")
step("one heat-carrying phonon MFP (300 nm)", MFP_HEAT, alpha_si,
     "the shortest length at which Fourier conduction starts to mean anything")
step("through the dense low-k stack (3 um)", 3e-6, alpha_lowk, "the wire's own heat path")
step("half a 300 um die", 150e-6, alpha_si, "die to spreader")
step("across one shire (1 mm, lateral)", 1e-3, alpha_si, "what the camera sees move")
out["ladder"] = ladder

# ballistic, for the steps where diffusion does not apply
out["ladder"]["ballistic"] = {
    "optical_phonon_lifetime_s": TAU_OPT,
    "optical_travel_in_one_lifetime_nm": V_OPT * TAU_OPT * 1e9,
    "heat_phonon_lifetime_s": TAU_HEAT,
    "heat_phonon_MFP_nm": MFP_HEAT * 1e9,
    "implied_velocity_m_per_s": MFP_HEAT / TAU_HEAT,
    "electron_inelastic_MFP_nm": [MFP_E_LO * 1e9, MFP_E_HI * 1e9],
    "electron_phonon_scattering_time_s": [TAU_EPH_LO, TAU_EPH_HI],
}

# E63's board, and how its phases are to be quoted.  Corrected Tue 27 Oct 2026 after review:
# the first version wrote "87-151 degrees", which mixed two different measurements, and read a
# 61 s pole off the 87 degrees without citing the repo's own 12 s single-pole read.
out["ladder"]["E63_board"] = {
    "pooled_complex_transfer": {
        "0.05_Hz": {"mK_per_W": 52.7, "sigma": 2.0, "phase_deg": 95.0},
        "0.15_Hz": {"mK_per_W": 18.4, "sigma": 5.4, "phase_deg": 151.0},
        "ratio": 18.4 / 52.7,
        "ratio_sigma": (18.4 / 52.7) * math.sqrt((5.4 / 18.4) ** 2 + (2.0 / 52.7) ** 2),
    },
    "the_drift_at_0p05_Hz": {"transfer_mK_per_W": [59.0, 52.9, 47.8, 42.4],
                             "phase_deg": [87.0, 109.0],
                             "what": "one hour, four top-rung blocks, board and camera warming"},
    "repo_roll_off_read": {"single_pole_s": 12.0, "lower_bound_1sigma_s": 3.2,
                           "upper_bound": None,
                           "note": "05-claims.md: 'a single pole of 12 s, or any pole longer "
                                   "(1 sigma: tau >= 3.2 s, with no upper bound)'.  At the "
                                   "pooled 95 degrees no single pole exists at all"},
    "phase_only_order_of_magnitude": {
        "from_phase_deg": 87.0, "at_Hz": 0.05,
        "one_pole_tau_s": math.tan(math.radians(87.0)) / (2 * math.pi * 0.05),
        "caveat": "a phase-only read of the ONE value just under 90 degrees, and a diffusive "
                  "path is not one pole.  The repo's 12 s amplitude read is the one to quote",
    },
}

# how much slower the camera is than the die's own path, with its own endpoints.  Corrected
# Tue 27 Oct 2026: "10^3 to 10^5" contained neither endpoint.
_t_die_vert = 150e-6 ** 2 / alpha_si
_t_shire_lat = 1e-3 ** 2 / alpha_si
_ratios = [(1.0 / f) / t for f in (0.05, 0.15) for t in (_t_die_vert, _t_shire_lat)]
out["ladder"]["camera_vs_die"] = {
    "die_vertical_s": _t_die_vert,
    "shire_lateral_s": _t_shire_lat,
    "lockin_periods_s": {"0.05_Hz": 20.0, "0.15_Hz": 1 / 0.15},
    "slower_by": {"min": min(_ratios), "max": max(_ratios)},
    "quote_as": "6 x 10^2 to 8 x 10^4",
    "to_resolve_the_die_Hz": 1.0 / _t_die_vert,
    "to_resolve_the_die_Hz_band": [1.0 / (2 * math.pi * _t_die_vert), 1.0 / _t_die_vert],
    "band_note": "1/(2 pi tau) to 1/tau for the 0.25 ms vertical path: of order a kilohertz",
}

# ---------------------------------------------------------------------------
# 8. the wire: where is a flip's heat actually born?
# ---------------------------------------------------------------------------
wire_len_um = (NET_SIG_C * 0.856 / 2.233) / C_SIG_PER_UM   # between-cell wire, um
r_on = VDD / IDSAT_NFIN
r_wire = R_SIG_PER_UM * wire_len_um
wire = {
    "C_per_um_F": C_SIG_PER_UM,
    "R_per_um_ohm": R_SIG_PER_UM,
    "R_per_um_is": "the ORFS AVERAGE SIGNAL wire (set_wire_rc -signal), not the tightest "
                   "metal -- corrected Tue 27 Oct 2026 after review",
    "between_cell_C_F": NET_SIG_C * 0.856 / 2.233,
    "between_cell_only": "this prices the BETWEEN-cell wire alone.  The 78.2% wire share of "
                         "the net's capacitance also counts 0.892 fF of in-cell wire, whose "
                         "resistance is not in this split at all (and which Q128 warns is "
                         "Miller charge moving to the output, not capacitance on the net)",
    "implied_length_um": wire_len_um,
    "R_on_one_fin_ohm": r_on,
    "R_wire_ohm": r_wire,
    "wire_share_of_dissipation_lumped": r_wire / (r_on + r_wire),
    "wire_share_of_dissipation_distributed": (r_wire / 2) / (r_on + r_wire / 2),
    "RC_per_um2_s": R_SIG_PER_UM * C_SIG_PER_UM,
    "Cu_electron_MFP_nm": CU_MFP * 1e9,
    "M1_width_nm": M1_W * 1e9,
    "MFP_over_width": CU_MFP / M1_W,
    "Cu_kappa_from_Wiedemann_Franz_300K": LORENZ * 300.0 / CU_RHO,
    "lowk_vs_Si_kappa_ratio": SI_K_300 / LOWK_K_DENSE,
    "lowk_porous_vs_Si_kappa_ratio": SI_K_300 / LOWK_K_POROUS,
    "fin_vs_bulk_kappa_ratio": SI_K_300 / SI_K_FIN,
}

# --- the two choices that move the share by more than its own precision.  Added Tue 27 Oct
# 2026 after review: the first version quoted 0.47% / 1,085 um flat on a ONE-fin driver and the
# average-signal layer, and called 26.6 ohm/um "tightest metal".
#   driver fins: 1 is the single minimum device; 6 is INVx1 and the repo's mix-weighted 6.09
#   per driven pin; charging 2.233 fF to 0.517 V inside this design's own 23 ps edge needs
#   >= C V / t = 50.2 uA, i.e. >= 1.4 fins, so one fin cannot do it.
#   layers: the average signal wire is what the estimator hands the net; M2 is the tightest
#   layer that carries signal routing here; M1 is the tightest in the stack but ORFS gives it
#   ~zero capacitance, so a net is never on it.
LAYERS = {"avg_signal": R_SIG_PER_UM, "M2": R_M2_PER_UM, "M1": R_M1_PER_UM, "M8": R_M8_PER_UM}
wire["min_current_to_charge_the_net_in_one_edge_A"] = NET_SIG_C * VDD / EDGE_RISE
wire["min_fins_from_that_current"] = (NET_SIG_C * VDD / EDGE_RISE) / IDSAT_NFIN
wire["fins_per_driven_pin_repo"] = FINS_PER_DRIVEN_PIN
wire["INVx1_nfin"] = INVX1_NFIN
wire["sensitivity"] = {}
for lname, rpu in LAYERS.items():
    rw = rpu * wire_len_um
    per_layer = {"R_per_um_ohm": rpu, "R_wire_ohm": rw, "by_driver_fins": {}}
    for n in (1, 2, 6):
        rdrv = r_on / n
        per_layer["by_driver_fins"][n] = {
            "R_driver_ohm": rdrv,
            "wire_share_distributed": (rw / 2) / (rdrv + rw / 2),
            "channel_share_distributed": rdrv / (rdrv + rw / 2),
            "crossover_length_um": 2 * rdrv / rpu,
        }
    wire["sensitivity"][lname] = per_layer
wire["headline"] = {
    "central": "6-fin driver (INVx1, and the repo's 6.09 fins per driven pin) on the average "
               "signal wire",
    "channel_share_central": wire["sensitivity"]["avg_signal"]["by_driver_fins"][6][
        "channel_share_distributed"],
    "channel_share_range_over_fins_and_layers": [
        min(wire["sensitivity"][l]["by_driver_fins"][n]["channel_share_distributed"]
            for l in ("avg_signal", "M2", "M1") for n in (1, 2, 6)),
        max(wire["sensitivity"][l]["by_driver_fins"][n]["channel_share_distributed"]
            for l in ("avg_signal", "M2", "M1") for n in (1, 2, 6)),
    ],
    "crossover_range_um_signal_layers": [
        min(wire["sensitivity"][l]["by_driver_fins"][n]["crossover_length_um"]
            for l in ("avg_signal", "M2") for n in (1, 2, 6)),
        max(wire["sensitivity"][l]["by_driver_fins"][n]["crossover_length_um"]
            for l in ("avg_signal", "M2") for n in (1, 2, 6)),
    ],
}

# --- the slab cross-check, restated.  Added Tue 27 Oct 2026 after review: the first version
# said 26.6 ohm/um "agrees within 2x with a slab at a few times bulk copper resistivity",
# which is self-refuting -- at a few times bulk the slab is ~79 ohm/um, 3x the ORFS value.
# The slab at 1x bulk IS the ORFS average.  The height is assumed (aspect ratio 2), not a kit
# number: ASAP7's 1x tech LEF carries no layer thickness.
slab_area = M1_W * (2 * M1_W)
wire["slab_cross_check"] = {
    "cross_section_nm": [M1_W * 1e9, 2 * M1_W * 1e9],
    "aspect_ratio_assumed": 2.0,
    "area_m2": slab_area,
    "R_per_um_at_bulk_Cu_ohm": CU_RHO * 1e-6 / slab_area,
    "ORFS_avg_signal_over_that": R_SIG_PER_UM / (CU_RHO * 1e-6 / slab_area),
    "ORFS_M1_over_that": R_M1_PER_UM / (CU_RHO * 1e-6 / slab_area),
    "reading": "the ORFS average-signal value is what a BULK-resistivity conductor of that "
               "cross-section gives (1.0x).  M1's own value is 2.7x it, which is where the "
               "narrow-wire resistivity rise of section 3 shows up.  Both statements hold, on "
               "different layers",
}

# --- Q129(a)'s extraction, as a declared sensitivity (not re-baselined)
bc_extracted = (NET_SIG_C * 0.856 / 2.233) / STEINER_OVER_EXTRACTED
net_extracted = NET_SIG_C - (NET_SIG_C * 0.856 / 2.233) + bc_extracted
wire["if_Q129a_extraction_is_used"] = {
    "steiner_over_extracted": STEINER_OVER_EXTRACTED,
    "between_cell_C_F": bc_extracted,
    "length_um": bc_extracted / C_SIG_PER_UM,
    "average_net_C_F": net_extracted,
    "net_change": net_extracted / NET_SIG_C - 1.0,
    "x_floor_80C_edge": (0.5 * net_extracted * VDD**2) / kt_ln2(T_LEAK),
    "optical_phonons_per_edge": (0.5 * net_extracted * VDD**2) / (E_OPT * QE),
    "note": "Q128's published ledger is still 2.233 fF, so the note's numbers stay on it and "
            "this row says what moves if the extraction replaces the Steiner estimate",
}
out["wire"] = wire

# ---------------------------------------------------------------------------
# 9. what a whole MAC looks like in phonons and atoms
# ---------------------------------------------------------------------------
mac_rail = MAC_BOARD * RAIL_SHARE
out["mac"] = {
    "board_J": MAC_BOARD,
    "rail_J": mac_rail,
    "optical_phonons_rail": mac_rail / e_opt_J,
    "net_toggles": NET_SIG_TOGGLES + NET_CLK_TOGGLES,
    "electrons_rail": mac_rail / (QE * VDD),
    "x_floor_66C": MAC_BOARD / kt_ln2(T_TRIP),
    "at_9p18_TFLOPS_MAC_per_s": 9.18e12 / 2,
    "phonons_per_second_rail": (mac_rail / e_opt_J) * (9.18e12 / 2),
    # the rail share is a range, not a constant.  Corrected Tue 27 Oct 2026: the count was
    # quoted to three figures on 0.75 alone.  Two figures, with the registered spread.
    "rail_share_used": RAIL_SHARE,
    "rail_share_range": [RAIL_SHARE_LO, RAIL_SHARE_HI],
    "optical_phonons_rail_range": [MAC_BOARD * RAIL_SHARE_LO / e_opt_J,
                                   MAC_BOARD * RAIL_SHARE_HI / e_opt_J],
    "quote_as": "4.2 x 10^8 on the 0.75 share; 3.9-5.0 x 10^8 over the registered 0.70-0.89",
}

SOURCES = [
    "Pop, Sinha, Goodson, Proc. IEEE 94(8) 1587-1601 (2006), doi:10.1109/JPROC.2006.879794",
    "Cahill, Wang, Kang, Watanabe, Koh, Letcher, Daly, 'Phonon lifetimes in silicon from "
    "50 GHz to 15 THz', MRS Fall 2009; primary: APL 90 252104 (2007), PRB 80 174112 (2009), "
    "PRB 71 235202 (2005), JAP 104 024905 (2008)",
    "Regner et al., Nat. Commun. 4, 1640 (2013), doi:10.1038/ncomms2630",
    "Yoo, Kim, Kang, Shin, J. Semicond. Technol. Sci. 16(2) 204-209 (2016), "
    "doi:10.5573/JSTS.2016.16.2.204",
    "Prasad, Ramey, Jiang, IRPS 2017 6A-4.1-6A-4.7, doi:10.1109/IRPS.2017.7936336",
    "Karmokar, Tam, Dinh, Chhabria, Harjani, Sapatnekar, ICCAD 2024, doi:10.1145/3676536.3676829",
    "Chhabria, Sapatnekar, ISQED 2019 235-240, doi:10.1109/ISQED.2019.8697786",
    "Alam, Pulavarthy, Bielefeld, King, Haque, J. Electron. Mater. 43(3) 746-754 (2014), "
    "doi:10.1007/s11664-013-2949-5",
    "Gall, J. Appl. Phys. 119, 085101 (2016), doi:10.1063/1.4942216",
    "Clark et al., Microelectronics Journal 53, 105-115 (2016), doi:10.1016/j.mejo.2016.04.006",
    "Glassbrenner, Slack, Phys. Rev. 134, A1058 (1964), doi:10.1103/PhysRev.134.A1058",
    "Landauer, IBM J. Res. Dev. 5, 183 (1961), doi:10.1147/rd.53.0183",
    "OpenROAD-flow-scripts, flow/platforms/asap7 (setRC.tcl, asap7_tech_1x_201209.lef)",
]
out["sources"] = SOURCES


def main() -> int:
    # always writes atoms.json next to this file; --no-json skips it (useful when auditing
    # the committed artifact from a scratch copy)
    here = os.path.dirname(os.path.abspath(__file__))
    if "--no-json" not in sys.argv:
        with open(os.path.join(here, "atoms.json"), "w") as fh:
            json.dump(out, fh, indent=1, sort_keys=False)
    print("== floors, kT ln 2 ==")
    for t, d in floors.items():
        print(f"  {t:5.1f} C  {d['kT_ln2_J']*1e21:7.3f} zJ   "
              f"one electron across {VDD} V = {d['one_electron_x_floor']:6.2f} x floor")
    print("\n== the plan's 25,000x ==")
    print(f"  quoted           {plan['quoted']}")
    print(f"  reproduced       {plan['reproduced']:.0f}  (via its 2,000 e-)")
    print(f"  direct 83aJ/floor{plan['direct_ratio']:9.0f}  "
          f"(the 0.2% between them is 83/82.85, rounding)")
    fl = plan["from_the_liberty_value"]
    print(f"  its C is SOURCED: ASAP7's INVx1 liberty input pin "
          f"{INVX1_PIN_LIB_C*1e15:.4f} fF -> {fl['E_edge_J']*1e18:.2f} aJ/edge, "
          f"{fl['electrons']:.0f} e-")
    print(f"  exact: {fl['x_floor_80C']:.0f}x at 80 C, {fl['x_floor_58C']:.0f}x at 58 C "
          f"(05-claims.md's settled ~26,000x)")
    v = plan["liberty_pin_vs"]
    print(f"  that pin is {v['one_minimum_fin_bare_gate']:.1f}x one minimum fin's bare gate, "
          f"{v['INVx1_six_fins_of_bare_gate']:.2f}x INVx1's six fins of bare gate, "
          f"{v['INVx1_same_pin_in_SPICE']:.2f}x the same pin in SPICE, "
          f"{v['the_average_signal_net']:.3f}x the average net")
    w = plan["what_it_prices"]["INVx1_is_not_the_minimum_inverter"]
    print(f"  and INVx1 is not minimum: nfin {w['INVx1_nfin']} against INVxp33's "
          f"{w['INVxp33_nfin']}, leakage ratio {w['leakage_ratio']:.3f}")
    print("\n== every ratio the pages print, one table ==")
    for r in rows:
        print(f"  {r['x_floor']:12.4g} x  ({r['convention']:5s} @ {r['floor_C']:.0f} C)  "
              f"{r['energy_J']:.4g} J   {r['event']}")
    print("\n== phonons ==")
    print(f"  Si optical mode {E_OPT*1e3:.1f} meV ({ph['optical_mode_THz']:.1f} THz)")
    print(f"  per electron: {ph['phonons_per_electron_full_rail']:.2f} over the full rail, "
          f"{ph['phonons_per_electron_per_edge']:.2f} per edge")
    for k, v in ph["per_event"].items():
        print(f"  {v['optical_phonons']:12.4g} phonons  {k}")
    print("\n== the fin ==")
    print(f"  channel under one gate: {fin['volume_channel_nm3']:.0f} nm^3, "
          f"{fin['atoms_channel']:.0f} Si atoms")
    print(f"  atoms per electron on the gate: {fin['atoms_per_electron_channel']:.0f}")
    print(f"  dopants at 1e17 / 1e18 cm^-3: {fin['dopants_at_1e17_per_cm3']:.2f} / "
          f"{fin['dopants_at_1e18_per_cm3']:.2f}")
    for k, v in fin["dT_if_deposited"].items():
        print(f"  dT if deposited ({k}): channel {v['channel_K']:.3g} K "
              f"({v['channel_per_fin_if_6_fin_driver_K']:.3g} K over 6 fins), "
              f"block {v['block_K']:.3g} K, 10 nm drain cube {v['drain_10nm_cube_K']:.3g} K; "
              f"{v['energy_per_channel_atom_meV']:.4g} meV per atom = "
              f"{v['energy_per_channel_atom_over_kT66']:.3g} kT")
    lv = fin["lumped_model_volume"]
    print(f"  a 1 ns lumped tau at {RTH_YOO_300:.0f} K/W implies C_th "
          f"{lv['C_th_implied_J_per_K']:.3g} J/K = a cube {lv['cube_side_nm']:.0f} nm on a side")
    print("\n== self-heating ==")
    print(f"  mean power during one 23 ps edge: {p_edge*1e6:.2f} uW -> "
          f"quasi-steady {sh['quasi_steady_dT_if_Rth_applied_K']*1e3:.2f} mK at "
          f"{RTH_YOO_300:.0f} K/W")
    print(f"  one fin at Idsat: {sh['one_fin_at_Idsat']['power_W']*1e6:.1f} uW -> "
          f"{sh['one_fin_at_Idsat']['dT_K']*1e3:.1f} mK")
    print(f"  a net at 10% activity, 800 MHz: "
          f"{sh['a_net_toggling_at_10pc_800MHz']['power_W']*1e9:.1f} nW -> "
          f"{sh['a_net_toggling_at_10pc_800MHz']['dT_K']*1e6:.1f} uK")
    print("\n== the ladder ==")
    for s in ladder["steps"]:
        print(f"  {s['length_m']*1e9:10.1f} nm -> {s['time_s']:.3g} s   {s['what']}")
    e63 = out["ladder"]["E63_board"]
    print(f"  E63's board: pooled 52.7 mK/W at 95 deg against 18.4 at 151 deg; the repo reads "
          f"a {e63['repo_roll_off_read']['single_pole_s']:.0f} s single pole "
          f"(tau >= {e63['repo_roll_off_read']['lower_bound_1sigma_s']} s, no upper bound)")
    print(f"  phase-only read of the 87 deg drift value: "
          f"{e63['phase_only_order_of_magnitude']['one_pole_tau_s']:.1f} s "
          f"(order of magnitude, not a fit)")
    cv = out["ladder"]["camera_vs_die"]
    print(f"  the camera is {cv['slower_by']['min']:.0f}x to {cv['slower_by']['max']:.0f}x "
          f"slower than the die's own path ({cv['quote_as']})")
    print("\n== the wire ==")
    print(f"  between-cell wire {wire['implied_length_um']:.2f} um, "
          f"R {wire['R_wire_ohm']:.0f} ohm (ORFS AVERAGE SIGNAL wire) against one fin's "
          f"{wire['R_on_one_fin_ohm']/1e3:.1f} kohm")
    print(f"  the net needs >= {wire['min_current_to_charge_the_net_in_one_edge_A']*1e6:.1f} uA "
          f"in one 23 ps edge = >= {wire['min_fins_from_that_current']:.1f} fins; INVx1 has "
          f"{INVX1_NFIN} and the repo's mix is {FINS_PER_DRIVEN_PIN:.2f}")
    print("  wire share of the heat, by driver fins and layer:")
    for lname in ("avg_signal", "M2", "M1", "M8"):
        row = wire["sensitivity"][lname]["by_driver_fins"]
        print(f"    {lname:10s}  " + "  ".join(
            f"{n} fin {row[n]['wire_share_distributed']*100:5.2f}%" for n in (1, 2, 6)))
    print("  crossover length (um), same grid:")
    for lname in ("avg_signal", "M2", "M1", "M8"):
        row = wire["sensitivity"][lname]["by_driver_fins"]
        print(f"    {lname:10s}  " + "  ".join(
            f"{n} fin {row[n]['crossover_length_um']:7.0f}" for n in (1, 2, 6)))
    hd = wire["headline"]
    print(f"  so the channel's share is {hd['channel_share_central']*100:.1f}% centrally, "
          f"{hd['channel_share_range_over_fins_and_layers'][0]*100:.0f}-"
          f"{hd['channel_share_range_over_fins_and_layers'][1]*100:.1f}% over the grid")
    sc = wire["slab_cross_check"]
    print(f"  slab check: 18 x 36 nm at BULK Cu = {sc['R_per_um_at_bulk_Cu_ohm']:.1f} ohm/um, "
          f"ORFS avg {sc['ORFS_avg_signal_over_that']:.2f}x it, M1 {sc['ORFS_M1_over_that']:.2f}x")
    q9 = wire["if_Q129a_extraction_is_used"]
    print(f"  if Q129(a)'s extraction replaces the Steiner estimate: net "
          f"{q9['average_net_C_F']*1e15:.3f} fF ({q9['net_change']*100:+.1f}%), "
          f"{q9['x_floor_80C_edge']:.0f}x the 80 C floor")
    print(f"  Cu electron MFP {wire['Cu_electron_MFP_nm']:.1f} nm against an "
          f"{wire['M1_width_nm']:.0f} nm wire = {wire['MFP_over_width']:.2f}x")
    print(f"  kappa: Si {SI_K_300:.0f}, narrow fin {SI_K_FIN:.0f}, dense low-k "
          f"{LOWK_K_DENSE}, porous low-k {LOWK_K_POROUS} W/(m K)")
    print("\n== one random MAC ==")
    print(f"  rail {out['mac']['rail_J']*1e12:.3f} pJ = "
          f"{out['mac']['optical_phonons_rail']:.3g} optical phonons, "
          f"{out['mac']['x_floor_66C']:.3g} x the floor")
    print(f"  at 9.18 TFLOPS: {out['mac']['phonons_per_second_rail']:.3g} phonons a second")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
