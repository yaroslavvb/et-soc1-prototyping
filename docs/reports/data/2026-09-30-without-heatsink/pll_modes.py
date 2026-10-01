#!/usr/bin/env python3
"""ET-SoC-1 clock and voltage facts decoded from the firmware sources (read-only; touches no card).

Reads the Movellus PLL mode tables that BL2 programs (etsoc-hal hpdpll_modes_config.h and lvdpll_modes_config.h),
the PMIC voltage encodings and range checks of each BL2 build, and prints:
  1. every HPDPLL mode with a 100 MHz reference (the set DM_CMD_SET_FREQUENCY accepts for the NoC PLL, and for the
     minions when use_step_clock = 1, which the stock dev_mngt_service always sends);
  2. the LVDPLL (per-shire PLL) range, which the firmware does not use for the minions (errata 7.3);
  3. the boot modes of each PLL;
  4. what post-divider a 50, 25 or 10 MHz output would need at the DCO frequencies the tables use, against the
     divider field widths in the Movellus IP-XACT headers (hardware headroom only: no table entry exists);
  5. the rail range checks of BL2 0.18.0 / 0.20.0 / 0.21.0 / HEAD in code and mV, and the safe-state voltages.

Output = source facts plus arithmetic on them (decoding register values). Run: python3 pll_modes.py
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def find_platform():
    cands = [os.path.join(HERE, *([".."] * k), "external", "et-platform") for k in range(1, 6)]
    for c in cands:
        if os.path.isdir(os.path.join(c, "etsoc-hal")):
            return os.path.normpath(c)
    sys.exit("external/et-platform not found")


EP = find_platform()
HW = os.path.join(EP, "etsoc-hal", "include", "hwinc")
IPX = os.path.join(EP, "etsoc-hal", "include", "etsoc_hal", "inc")


def parse_modes(fn):
    """Return [{line, mode, in, out, regs{offset: value}}] from a *_modes_config.h table."""
    lines = open(os.path.join(HW, fn)).read().split("\n")
    rows, cur = [], None
    for i, l in enumerate(lines, 1):
        m = re.search(r"\.mode\s*=\s*(\d+)", l)
        if m:
            cur = {"line": i, "mode": int(m.group(1))}
            continue
        if cur is None:
            continue
        for k, key in (("input_frequency", "in"), ("output_frequency", "out")):
            m = re.match(r"\s*\.%s\s*=\s*(\d+)" % k, l)
            if m:
                cur[key] = int(m.group(1)) / 1e6
        if re.match(r"\s*\.offsets\s*=", l):
            cur["offs"] = [int(x, 16) for x in re.findall(r"0x[0-9a-fA-F]+", l + lines[i])]
        if re.match(r"\s*\.values\s*=", l):
            vals = [int(x, 16) for x in re.findall(r"0x[0-9a-fA-F]+", l + lines[i])]
            cur["regs"] = dict(zip(cur.pop("offs"), vals))
            rows.append(cur)
            cur = None
    for r in rows:  # FCW_INT reg 0x2, FCW_FRAC reg 0x3, POSTDIV0 reg 0xE (hpdpll_register_defines.h:14-24)
        g = r["regs"]
        r["dco"] = r["in"] * (g.get(2, 0) + g.get(3, 0) / 65536)
        r["pd"] = g.get(0xE, 0)
        assert abs(r["dco"] / r["pd"] - r["out"]) < 0.5, r
    return rows


def ipx_width(fn, field):
    t = open(os.path.join(IPX, fn)).read()
    m = re.search(r"#define %s_WIDTH (\d+)u" % field, t)
    return int(m.group(1)), t[: m.start()].count("\n") + 1


hp = parse_modes("hpdpll_modes_config.h")
lv = parse_modes("lvdpll_modes_config.h")
hp100 = sorted([r for r in hp if r["in"] == 100], key=lambda r: (r["out"], r["mode"]))
lv100 = [r for r in lv if r["in"] == 100]

print("== 1. HPDPLL modes with a 100 MHz reference (etsoc-hal/include/hwinc/hpdpll_modes_config.h)")
print("   %d of %d entries; SET_FREQUENCY takes the FIRST table entry whose output equals the request "
      "(thermal_power_monitor.c pwr_svc_find_hpdpll_mode)" % (len(hp100), len(hp)))
seen = set()
for r in hp100:
    dup = "" if r["out"] not in seen else "  (duplicate; never chosen)"
    seen.add(r["out"])
    print("   %7.1f MHz  mode %3d  line %4d  DCO %6.1f MHz / postdiv %2d%s" % (r["out"], r["mode"], r["line"], r["dco"], r["pd"], dup))
below300 = [r for r in hp100 if r["out"] < 300]
print("   below 300 MHz: %s MHz" % ", ".join("%g" % r["out"] for r in below300))
print("   lowest: %g MHz (mode %d); highest: %g MHz" % (hp100[0]["out"], hp100[0]["mode"], hp100[-1]["out"]))

print("\n== 2. LVDPLL (per-shire minion PLL) modes, 100 MHz reference (lvdpll_modes_config.h)")
print("   %d entries, %g-%g MHz in %g MHz steps; mode 1 = %g MHz at line %d" % (
    len(lv100), min(r["out"] for r in lv100), max(r["out"] for r in lv100),
    lv100[1]["out"] - lv100[0]["out"], lv100[0]["out"], lv100[0]["line"]))

print("\n== 3. Boot modes (BL2 main.c noc_pll_mode/min_step_pll_mode; io_pll.c; mem_controller.c)")
boot = [("NoC PLL2 (noc_pll_mode[0])", hp, 37), ("minion step clock PLL4 (min_step_pll_mode[0])", hp, 34),
        ("minion LVDPLL (min_lvdpll_mode[0], unused: step clock chosen)", lv, 1),
        ("SP PLL0 (PLL0_100_PERCENT_TARGET_MODE)", hp, 3), ("SP PLL1 (PLL1_100_PERCENT_TARGET_MODE)", hp, 1),
        ("PShire PLL (PSHR_PLL_50_PERCENT_TARGET_MODE)", hp, 54), ("memshire PLL 933 (min_lvdpll_mode_933MHz[0])", hp, 28),
        ("memshire PLL 795", hp, 50), ("memshire PLL 1066", hp, 19)]
for name, tab, mode in boot:
    r = [x for x in tab if x["mode"] == mode][0]
    print("   %-58s mode %3d -> %7.1f MHz (in %g)" % (name, mode, r["out"], r["in"]))

print("\n== 4. Hardware headroom below the tables (NOT reachable through any DM command)")
w_hp, l_hp = ipx_width("mvls_tn7_hpdpll.ipxact.h", "MVLS_TN7_HPDPLL_MAIN_MAIN_REGISTER14_POSTDIV0")
w_lv, l_lv = ipx_width("mvls_tn7_lvdpll.ipxact.h", "MVLS_TN7_LVDPLL_MAIN_MAIN_REGISTER14_POSTDIV0")
dco_hp = sorted(set(round(r["dco"]) for r in hp))
dco_lv = sorted(set(round(r["dco"]) for r in lv))
print("   HPDPLL POSTDIV0 width %d bits (max %d; mvls_tn7_hpdpll.ipxact.h:%d); DCO in tables %d-%d MHz" % (
    w_hp, 2 ** w_hp - 1, l_hp, dco_hp[0], dco_hp[-1]))
print("   LVDPLL POSTDIV0 width %d bits (max %d; mvls_tn7_lvdpll.ipxact.h:%d); DCO in tables %d-%d MHz" % (
    w_lv, 2 ** w_lv - 1, l_lv, dco_lv[0], dco_lv[-1]))
print("   largest post-divider any table entry uses: HPDPLL %d, LVDPLL %d" % (max(r["pd"] for r in hp), max(r["pd"] for r in lv)))
for f in (50, 25, 10):
    for name, lo, hi, w in (("HPDPLL", dco_hp[0], dco_hp[-1], w_hp), ("LVDPLL", dco_lv[0], dco_lv[-1], w_lv)):
        pd_lo, pd_hi = -(-lo // f), hi // f
        print("   %2d MHz via %s: post-divider %d-%d at the tables' DCO range; field max %d -> %s" % (
            f, name, pd_lo, pd_hi, 2 ** w - 1, "fits" if pd_lo <= 2 ** w - 1 else "does not fit"))
print("   minimum output at the lowest table DCO and the widest divider: HPDPLL %.2f MHz, LVDPLL %.2f MHz" % (
    dco_hp[0] / (2 ** w_hp - 1), dco_lv[0] / (2 ** w_lv - 1)))

print("\n== 5. Rail range checks (pmic_validate_voltage) and safe-state voltages, per BL2 build")
builds = [("0.18.0", "da192816a"), ("0.20.0", "ffca4cbb4"), ("0.21.0", "50310b06b"), ("HEAD", "836a4ab")]


def show(commit, path):
    try:
        return subprocess.run(["git", "-C", EP, "show", "%s:%s" % (commit, path)], capture_output=True,
                              text=True, check=True).stdout
    except subprocess.CalledProcessError:
        return ""


BASE = {"SRM": (250, 5, 1), "DDR": (250, 5, 1), "MXN": (250, 5, 1), "NOC": (250, 5, 1), "MNN": (250, 5, 1),
        "VDDQLP": (250, 10, 1), "VDDQ": (250, 10, 1), "PCL": (600, 625, 100), "PCIE": (600, 125, 10)}
for label, c in builds:
    h = show(c, "device-bootloaders/src/ServiceProcessorBL2/include/bl2_pmic_controller.h")
    t = show(c, "device-bootloaders/src/ServiceProcessorBL2/include/thermal_pwr_mgmt.h")
    lim = {}
    for m in re.finditer(r"#define (\w+)_(MIN|MAX)_VAL_mV \(([\d.]+)\)", h):
        lim.setdefault(m.group(1), {})[m.group(2)] = float(m.group(3))
    safe = {m.group(1): int(m.group(2), 16) for m in re.finditer(r"#define SAFE_STATE_(\w+)_VOLTAGE (0x[0-9A-Fa-f]+)", t)}
    sf = re.search(r"#define SAFE_STATE_FREQUENCY (\d+)", t)
    print("   BL2 %s (%s):" % (label, c))
    if not lim:
        print("      no per-rail range check in the PMIC driver")
    for rail in ("MNN", "SRM", "NOC", "DDR", "MXN", "PCL", "PCIE", "VDDQLP", "VDDQ"):
        if rail in lim:
            print("      %-6s %7.2f - %7.2f mV" % (rail, lim[rail]["MIN"], lim[rail]["MAX"]))
    for k, v in safe.items():
        mv = 250 + 5 * v
        note = ""
        if k == "L2CACHE" and "SRM" in lim and mv < lim["SRM"]["MIN"]:
            note = "  <-- below this build's own SRAM minimum %g mV" % lim["SRM"]["MIN"]
        print("      SAFE_STATE_%s_VOLTAGE 0x%02X = %d mV at SAFE_STATE_FREQUENCY %s MHz%s" % (k, v, mv, sf.group(1) if sf else "?", note))
print("   code -> mV: 250 + 5*code for minion/SRAM/NoC/DDR/Maxion (PMIC_*_VOLTAGE_BASE/MULTIPLIER); code 0 = 250 mV")

print("\n== 6. Small derived figures (inputs are recorded measurements; arithmetic only)")
# docs/findings/16-dvfs-and-leakage.md "What it costs": aifoundry2 after 20.6 h idle at 73.0 C, minion rail 11.05 W,
# SRAM 2.00 W, mesh 3.64 W, off-rail 15.10 W, board 31.79 W (E19, measured).
minion_w, sram_w, noc_w, off_w, board_w, n_shires = 11.05, 2.00, 3.64, 15.10, 31.79, 34
print("   idle minion rail per shire at 73 C: %.3f W (%.2f W / %d shires; no firmware power gating)" % (minion_w / n_shires, minion_w, n_shires))
print("   idle board power outside the minion clock domain (off-rail + NoC rail; the SRAM rail's shire caches share the"
      " minion clock, errata 2.30): %.0f%% (%.2f W of %.2f W)" % (100 * (off_w + noc_w) / board_w, off_w + noc_w, board_w))
# BL2 0.18.0 voltage law (minion_configuration.c @da192816a:1030-1110; THROTTLE_* at :267,:272; limits thermal_pwr_mgmt.h:61-66)
# with aifoundry1 card 1's boot set-points 500 mV minion / 750 mV SRAM at 600 MHz (reg_mv, claims-v3 raw telemetry, measured).
def v018(f, boot_mv, boot_f=600, lo=400, hi=650):
    mv = boot_mv - ((boot_f - f) // 50) * 10 if f < boot_f else boot_mv + ((f - boot_f) // 50) * 10
    return max(lo, min(hi, mv))
for f in (300, 200, 100):
    print("   0.18.0 law at %3d MHz: minion %d mV, SRAM %d mV (if its governor acted; card 1's is inactive)" % (
        f, v018(f, 500), v018(f, 750, lo=650, hi=1000)))
