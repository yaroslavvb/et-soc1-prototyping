#!/usr/bin/env python3
"""E128's device-command audit at the build card 1 actually runs (desk, read-only git reads of the public et-platform clone).

Written by the fix pass after verification, Mon 2 Nov 2026 (Q136). dmcmd-e128.py read the BL2 0.18.0 line because the
registration took card 1 to run firmware 1.2.0; but card 1 has reported release 1.4.0, BL1 and BL2 0.22.0, PMIC 1.3.0
since 31 Oct 2026 (E82 A1: docs/reports/data/2026-10-31-e82-kinds-aifoundry1/ident/firmware_pre.txt;
docs/findings/14-card-behaviour.md, the firmware table). So the version-matched source is et-platform 836a4ab
(device-bootloaders/CMakeLists.txt declares EsperantoBootLoader VERSION 0.22.0 there), the revision Q133's governor desk
and Q136(w)'s table (tools/claims-v3/dmcmd_table.json) use. For every function on each command's path this prints its
file:line at 836a4ab, whether it is the same as at da192816a (the 0.18.0 line's last commit, which dmcmd-e128.py read),
and every statement that stores somewhere other than a local, sorted by dmcmd-e128.py's own categories. It also prints
every caller of pvt_hilo_reset (the PVT high/low reset), to show the statistics getter does not reach it.

    python3 dmcmd-e128-022.py <et-platform clone> > dmcmd-e128-022.txt
SPDX-License-Identifier: Apache-2.0
"""
import re
import subprocess
import sys

REPO = sys.argv[1]
REV, OLD = "836a4ab60", "da192816a"   # BL2 0.22.0 (the running build) / the 0.18.0 line's last commit (dmcmd-e128.py's)
B = "device-bootloaders/src/ServiceProcessorBL2"
API = "device-api/include/management-api/device_mgmt_api_spec.h"
TPM, TPW, PRF, PMG = "services/thermal_power_monitor.c", "services/thermal_pwr_mgmt.c", "services/performance.c", "services/perf_mgmt.c"
PVT, PMIC, I2C = "driver/pvt_controller.c", "driver/pmic_controller.c", "driver/i2c_controller.c"
PMIC_READ = [(PMIC, "pmic_get_voltage"), (PMIC, "get_pmic_reg"), (PMIC, "wait_pmic_ready"), (I2C, "i2c_read")]
# (command, id) -> the functions on its path at 836a4ab: (file, name). The 0.22.0 path of command 53 adds
# calculate_pll_freq's strap read (reset.c get_hpdpll_strap_value); the PMIC reads add wait_pmic_ready (a GPIO read).
PATHS = {
    "DM_CMD_GET_MODULE_STATIC_TDP_LEVEL (25)": [(TPM, "pwr_svc_get_module_tdp_level"), (TPW, "get_module_tdp_level")],
    "DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS (21)": [(TPM, "pwr_svc_get_module_temp_thresholds"), (TPW, "get_module_temperature_threshold")],
    "DM_CMD_GET_MODULE_POWER_STATE (23)": [(TPM, "pwr_svc_get_module_power_state"), (TPW, "get_module_power_state")],
    "DM_CMD_GET_ASIC_FREQUENCIES (53)": [(PRF, "dm_svc_perf_get_asic_frequencies"), (PMG, "get_module_asic_frequencies"),
                                          ("driver/io_pll.c", "get_pll_frequency"), ("driver/io_pll.c", "calculate_pll_freq"),
                                          ("driver/reset.c", "get_hpdpll_strap_value"),
                                          ("driver/mem_controller.c", "get_memshire_frequency"), ("driver/mem_controller.c", "get_ddr_frequency")],
    "DM_CMD_GET_ASIC_VOLTAGE (32)": [(TPM, "pwr_svc_get_asic_voltage"), (TPW, "get_asic_voltage"),
                                     (PVT, "pvt_get_minion_avg_low_high_voltage"), (PVT, "pvt_get_min_shire_vm_sample"),
                                     (PVT, "pvt_get_memshire_avg_low_high_voltage"), (PVT, "pvt_get_memshire_vm_sample"),
                                     (PVT, "pvt_get_ioshire_vm_sample"), (PVT, "pvt_get_pshire_vm_sample")] + PMIC_READ,
    "DM_CMD_GET_MODULE_POWER (33)": [(TPM, "pwr_svc_get_module_power"), (TPW, "get_module_soc_power")],
    "DM_CMD_GET_SP_STATS (60)": [(PRF, "dm_svc_perf_get_sp_stats"), (TPW, "Thermal_Pwr_Mgmt_Get_System_Power_Temp_Stats")],
    "DM_CMD_GET_MODULE_CURRENT_TEMPERATURE (27)": [(TPM, "pwr_svc_get_module_current_temperature"), (TPW, "get_module_current_temperature"),
                                                   (PVT, "pvt_get_minion_avg_temperature"), (PVT, "pvt_get_minion_avg_low_high_temperature"),
                                                   (PVT, "pvt_get_ioshire_ts_sample"), (PVT, "pvt_get_min_shire_ts_sample"), (PVT, "pvt_get_ts_data")],
    "DM_CMD_GET_MODULE_VOLTAGE (31)": [(TPM, "pwr_svc_get_module_voltage"), (TPW, "get_module_voltage")] + PMIC_READ,
}
ROUTE = ("rtos_task/command_dispatcher.c", "pc_vq_process_pending_command")
MACROS = [(PVT, "GET_MINION_VM"), (PVT, "GET_MEMSHIRE_VM")]
IDS = ["DM_CMD_GET_MODULE_STATIC_TDP_LEVEL", "DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS", "DM_CMD_GET_MODULE_POWER_STATE",
       "DM_CMD_GET_ASIC_FREQUENCIES", "DM_CMD_GET_ASIC_VOLTAGE", "DM_CMD_GET_MODULE_POWER", "DM_CMD_GET_SP_STATS",
       "DM_CMD_GET_MODULE_CURRENT_TEMPERATURE", "DM_CMD_GET_MODULE_VOLTAGE",
       "DM_CMD_GET_MODULE_FIRMWARE_REVISIONS", "DM_CMD_SET_STATS_RUN_CONTROL", "DM_CMD_SET_DM_TRACE_CONFIG"]
# dmcmd-e128.py's categories, unchanged
CATS = [("a device register (the SP's I2C controller's command register: an I2C transaction)", re.compile(r"->regs->[A-Z_]+\s*=(?!=)")),
        ("a call that writes (error path or not: see the line)", re.compile(r"\b(i2c_soft_reset|set_pmic_reg|i2c_write|pmic_set_[a-z_]+|flash_fs_[a-z_]+|update_module_[a-z_]+|write_memshire_[a-z_]+|iowrite\w*)\s*\(")),
        ("SP RAM: a global (a copy of the value just read, or an error mark)", re.compile(r"\b(g_[a-z0-9_]+(\.[a-z0-9_\[\]]+)+|get_soc_perf_reg\(\)->[a-z0-9_.]+|pvt_bad_min_shire_mask)\s*(\|=|=)(?!=)"))]


def git(*a):
    return subprocess.run(["git", "-C", REPO] + list(a), check=True, capture_output=True, text=True).stdout


def body(rev, rel, name):
    """(1-based line, text) of the function's definition at rev, or (None, None)."""
    lines = git("show", f"{rev}:{B}/{rel}").split("\n")
    pat = re.compile(r"^(static\s+)?(inline\s+)?[A-Za-z_][A-Za-z_0-9 \*]*\b" + re.escape(name) + r"\s*\(")
    for i, l in enumerate(lines):
        if pat.match(l) and not l.rstrip().endswith(";"):
            depth, out, started = 0, [], False
            for l2 in lines[i:]:
                out.append(l2)
                depth += l2.count("{") - l2.count("}")
                if "{" in l2:
                    started = True
                if started and depth == 0:
                    return i + 1, "\n".join(out)
    return None, None


def macro(rev, rel, name):
    src = git("show", f"{rev}:{B}/{rel}").split("\n")
    for i, l in enumerate(src):
        if l.startswith(f"#define {name}("):
            out = []
            for l2 in src[i:]:
                out.append(l2)
                if not l2.rstrip().endswith("\\"):
                    return i + 1, "\n".join(out)
    return None, None


def stores(text):
    out = []
    for l in text.split("\n"):
        t = l.strip()
        if t.startswith(("*", "/*", "//")) or "Log_Write" in t or "MESSAGE_ERROR" in t:
            continue
        for cat, rx in CATS:
            if rx.search(t):
                out.append((cat, t.rstrip("\\ ").strip()))
                break
    return out


cm = [l for l in git("show", f"{REV}:device-bootloaders/CMakeLists.txt").split("\n") if "project(EsperantoBootLoader" in l]
print(f"E128 device-command audit at the running build. Public source: et-platform {REV} ({cm[0].strip() if cm else '?'}),")
print(f"compared function by function with {OLD} (the BL2 0.18.0 line's last commit, which dmcmd-e128.py read).")
api = git("show", f"{REV}:{API}")
idmap = {m.group(1): int(m.group(2)) for m in re.finditer(r"^\s*(DM_CMD_[A-Z0-9_]+)\s*=\s*(\d+)\s*,", api, re.M)}
print("Command ids at " + REV + ": " + ", ".join(f"{n[7:]} {idmap.get(n)}" for n in IDS))
ln, a_ = body(REV, *ROUTE)
_, b_ = body(OLD, *ROUTE)
added = [l.strip() for l in a_.split("\n") if l not in b_.split("\n")]
removed = [l.strip() for l in b_.split("\n") if l not in a_.split("\n")]
print(f"Routing: {ROUTE[1]} ({ROUTE[0]}:{ln}): same as at {OLD}: {a_ == b_}; lines added since: {added}; lines gone: {removed}")
print("The services' own switches at " + REV + " (each command's case and the call under it):")
for rel in (TPM, PRF):
    src = git("show", f"{REV}:{B}/{rel}").split("\n")
    for k, l in enumerate(src):
        m = re.match(r"\s*case (DM_CMD_[A-Z0-9_]+):", l)
        if m and m.group(1) in IDS[:9]:
            nxt = next((x.strip() for x in src[k + 1:k + 6] if x.strip() and not x.strip().startswith(("/*", "//", "{"))), "?")
            print(f"   {rel}:{k + 1} case {m.group(1)}: {nxt}")
print()
summary = {}
for cmd, path in PATHS.items():
    print(f"== {cmd}")
    cats = {}
    for rel, name in path:
        line, a = body(REV, rel, name)
        _, b = body(OLD, rel, name)
        st = stores(a or "")
        print(f"   {rel}:{line} {name}: found {a is not None}; same as at {OLD}: {a == b}; stores other than locals: {len(st)}")
        for cat, s in st:
            print(f"      | [{cat}] {s}")
            cats[cat.split(" (")[0]] = cats.get(cat.split(" (")[0], 0) + 1
    summary[cmd] = cats
    print()
for rel, name in MACROS:
    line, a = macro(REV, rel, name)
    _, b = macro(OLD, rel, name)
    st = stores(a or "")
    print(f"== macro {name} ({rel}:{line}): found {a is not None}; same as at {OLD}: {a == b}; stores other than locals: {len(st)}")
    for cat, s in st:
        print(f"      | [{cat}] {s}")
print()
print("Callers of pvt_hilo_reset (the PVT sensors' high/low reset) at " + REV + ":")
for hit in git("grep", "-n", r"pvt_hilo_reset\s*(", REV, "--", B).split("\n"):
    if not hit.strip() or "/include/" in hit:
        continue
    _, path, lno = hit.split(":", 3)[:3]
    rel = path[len(B) + 1:]
    src = git("show", f"{REV}:{path}").split("\n")
    if re.match(r"^[A-Za-z_][A-Za-z_0-9 \*]*\bpvt_hilo_reset\s*\(", src[int(lno) - 1]):
        print(f"   {rel}:{lno} (its definition)")
        continue
    fn = "?"
    for k in range(int(lno) - 1, -1, -1):
        m = re.match(r"^[A-Za-z_][A-Za-z_0-9 \*]*\b([A-Za-z_][A-Za-z_0-9]*)\s*\(", src[k])
        if m and not src[k].rstrip().endswith(";"):
            fn = m.group(1)
            break
    print(f"   {rel}:{lno} called in {fn}")
print()
print("Per command, the stores other than locals on its whole path, by category:")
for cmd, cats in summary.items():
    print(f"   {cmd}: " + (", ".join(f"{k}: {v}" for k, v in cats.items()) or "none"))
