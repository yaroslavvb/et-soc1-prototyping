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

# the 16 Oct outline's ruler rung that the 20 Oct plan's "25,000x" was built on
PLAN_INV_E_EDGE = 83e-18   # J   "minimum inverter input, 83 aJ"
PLAN_INV_NE = 2000         # electrons

# measured, on the card
E60_FLIP_BOARD = 116.7e-15     # J  one flipped fp32 MAC input bit, a = 1.0, board
E65_FLOWM_BOARD = 745e-15      # J  E65's flow-M flip, board
MAC_BOARD = 5.783e-12          # J  one random fp32 MAC over idle, board (E38)
MAC_LEDGER = 1.946e-12         # J  the bottom-up open ledger (Q128)
RAIL_SHARE = 0.75              # minion rail / board (E60)

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

# ORFS asap7 setRC.tcl (units are the liberty's: kohm/um and fF/um)
R_SIG_PER_UM = 26.5684     # ohm/um, average signal wire
C_SIG_PER_UM = 0.165790e-15  # F/um
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
LOWK_RHO_C = 1.3e6         # J/(m^3 K) ~ 1300 kg/m^3 x 1000 J/(kg K)
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
# 2. the 25,000x: reproduce it, then say what it was
# ---------------------------------------------------------------------------
# the plan's own factorisation: 1/2 C V^2 / (kT ln2) = (CV/e)(eV/kT)/(2 ln2)
plan = {
    "quoted": 24500,
    "inputs": {"electrons": PLAN_INV_NE, "eVDD_over_kT_80C": VDD / kt_ev(T_LEAK),
               "divisor_2ln2": 2 * LN2},
    "reproduced": PLAN_INV_NE * (VDD / kt_ev(T_LEAK)) / (2 * LN2),
    # what capacitance does 83 aJ of heat per edge imply?
    "C_implied_from_83aJ_F": 2 * PLAN_INV_E_EDGE / VDD**2,
    "C_implied_from_2000e_F": PLAN_INV_NE * QE / VDD,
    "direct_ratio": PLAN_INV_E_EDGE / kt_ln2(T_LEAK),
}
# how that capacitance compares with what Q128 then measured
plan["vs_one_fin_gate"] = plan["C_implied_from_83aJ_F"] / FIN_CGATE
plan["vs_INVx1_pin_2fin"] = plan["C_implied_from_83aJ_F"] / (2 * FIN_CGATE)
plan["vs_average_signal_net"] = plan["C_implied_from_83aJ_F"] / NET_SIG_C
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
    ratio_row("an INVx1's own input pin, 2 fins, heat per edge",
              2 * FIN_E_RISE / 2, "edge", T_LEAK, 2 * FIN_NE, 2 * FIN_CGATE),
    ratio_row("THE PLAN'S ROW: 'minimum inverter', C assumed 0.62 fF, heat per edge",
              PLAN_INV_E_EDGE, "edge", T_LEAK, PLAN_INV_NE,
              plan["C_implied_from_83aJ_F"]),
    ratio_row("CORRECTED: an INVx1 toggling this design's average signal net",
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

# E63's measured lag at the back of the board, read as one pole
f_lockin = 0.05
phase_deg = 87.0
out["ladder"]["E63_board"] = {
    "lockin_Hz": f_lockin,
    "phase_deg": phase_deg,
    "one_pole_tau_s": math.tan(math.radians(phase_deg)) / (2 * math.pi * f_lockin),
    "caveat": "a diffusive path is not one pole; this is an order-of-magnitude read",
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
    "between_cell_C_F": NET_SIG_C * 0.856 / 2.233,
    "implied_length_um": wire_len_um,
    "R_on_one_fin_ohm": r_on,
    "R_wire_ohm": r_wire,
    "wire_share_of_dissipation_lumped": r_wire / (r_on + r_wire),
    "wire_share_of_dissipation_distributed": (r_wire / 2) / (r_on + r_wire / 2),
    "crossover_length_um_tight_metal": 2 * r_on / R_SIG_PER_UM,
    "crossover_length_um_M8": 2 * r_on / R_M8_PER_UM,
    "RC_per_um2_s": R_SIG_PER_UM * C_SIG_PER_UM,
    "Cu_electron_MFP_nm": CU_MFP * 1e9,
    "M1_width_nm": M1_W * 1e9,
    "MFP_over_width": CU_MFP / M1_W,
    "Cu_kappa_from_Wiedemann_Franz_300K": LORENZ * 300.0 / CU_RHO,
    "lowk_vs_Si_kappa_ratio": SI_K_300 / LOWK_K_DENSE,
    "lowk_porous_vs_Si_kappa_ratio": SI_K_300 / LOWK_K_POROUS,
    "fin_vs_bulk_kappa_ratio": SI_K_300 / SI_K_FIN,
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
    here = os.path.dirname(os.path.abspath(__file__))
    if "--json" in sys.argv or True:
        with open(os.path.join(here, "atoms.json"), "w") as fh:
            json.dump(out, fh, indent=1, sort_keys=False)
    print("== floors, kT ln 2 ==")
    for t, d in floors.items():
        print(f"  {t:5.1f} C  {d['kT_ln2_J']*1e21:7.3f} zJ   "
              f"one electron across {VDD} V = {d['one_electron_x_floor']:6.2f} x floor")
    print("\n== the plan's 25,000x ==")
    print(f"  quoted           {plan['quoted']}")
    print(f"  reproduced       {plan['reproduced']:.0f}")
    print(f"  direct 83aJ/floor{plan['direct_ratio']:9.0f}")
    print(f"  C implied        {plan['C_implied_from_83aJ_F']*1e15:.3f} fF "
          f"(from 2,000 e-: {plan['C_implied_from_2000e_F']*1e15:.3f} fF)")
    print(f"  that is {plan['vs_one_fin_gate']:.1f}x one fin's gate, "
          f"{plan['vs_INVx1_pin_2fin']:.1f}x an INVx1 pin, "
          f"{plan['vs_average_signal_net']:.3f}x the average net")
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
    print(f"  E63's board, read as one pole: "
          f"{out['ladder']['E63_board']['one_pole_tau_s']:.1f} s")
    print("\n== the wire ==")
    print(f"  between-cell wire {wire['implied_length_um']:.2f} um, "
          f"R {wire['R_wire_ohm']:.0f} ohm against the driver's "
          f"{wire['R_on_one_fin_ohm']/1e3:.1f} kohm")
    print(f"  the wire's share of the heat: "
          f"{wire['wire_share_of_dissipation_distributed']*100:.2f} %")
    print(f"  crossover: {wire['crossover_length_um_tight_metal']:.0f} um on tight metal, "
          f"{wire['crossover_length_um_M8']:.0f} um on M8")
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
