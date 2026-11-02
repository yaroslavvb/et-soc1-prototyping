#!/usr/bin/env python3
"""E128's device-command audit (desk, read-only git reads of the public et-platform clone): every device-management command E128's run sends, the
service processor's handler for it on the BL2 0.18.0 line (aifoundry1 card 1 runs firmware 1.2.0, BL2 0.18.0), whether each function on the path is the
same at the line's first and last commits, and every statement on the path that stores somewhere other than a local variable, so the READ/WRITE class can
be read off the source. Standard library only.

    python3 dmcmd_e128.py <et-platform clone>  > dmcmd-e128.txt
SPDX-License-Identifier: Apache-2.0
"""
import re
import subprocess
import sys

REPO = sys.argv[1]
FIRST, LAST = "169a17566", "da192816a"          # EsperantoBootLoader VERSION 0.18.0 is declared from 169a17566; 29950410d declares 0.19.0; da192816a = 29950410d~1
B = "device-bootloaders/src/ServiceProcessorBL2"
# (command, id, the functions on its path: file, name)
PATHS = {
    "DM_CMD_GET_MODULE_STATIC_TDP_LEVEL (25)": [("services/thermal_power_monitor.c", "pwr_svc_get_module_tdp_level"), ("services/thermal_pwr_mgmt.c", "get_module_tdp_level")],
    "DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS (21)": [("services/thermal_power_monitor.c", "pwr_svc_get_module_temp_thresholds"), ("services/thermal_pwr_mgmt.c", "get_module_temperature_threshold")],
    "DM_CMD_GET_MODULE_POWER_STATE (23)": [("services/thermal_power_monitor.c", "pwr_svc_get_module_power_state"), ("services/thermal_pwr_mgmt.c", "get_module_power_state")],
    "DM_CMD_GET_ASIC_FREQUENCIES (53)": [("services/performance.c", "dm_svc_perf_get_asic_frequencies"), ("services/perf_mgmt.c", "get_module_asic_frequencies"),
                                          ("driver/io_pll.c", "get_pll_frequency"), ("driver/mem_controller.c", "get_memshire_frequency"), ("driver/mem_controller.c", "get_ddr_frequency")],
    "DM_CMD_GET_ASIC_VOLTAGE (32)": [("services/thermal_power_monitor.c", "pwr_svc_get_asic_voltage"), ("services/thermal_pwr_mgmt.c", "get_asic_voltage"),
                                     ("driver/pvt_controller.c", "pvt_get_minion_avg_low_high_voltage"), ("driver/pvt_controller.c", "pvt_get_min_shire_vm_sample"),
                                     ("driver/pvt_controller.c", "pvt_get_memshire_avg_low_high_voltage"), ("driver/pvt_controller.c", "pvt_get_memshire_vm_sample"),
                                     ("driver/pvt_controller.c", "pvt_get_ioshire_vm_sample"), ("driver/pvt_controller.c", "pvt_get_pshire_vm_sample"),
                                     ("driver/pmic_controller.c", "pmic_get_voltage"), ("driver/pmic_controller.c", "get_pmic_reg"), ("driver/i2c_controller.c", "i2c_read")],
    "DM_CMD_GET_MODULE_POWER (33)": [("services/thermal_power_monitor.c", "pwr_svc_get_module_power"), ("services/thermal_pwr_mgmt.c", "get_module_soc_power")],
    "DM_CMD_GET_SP_STATS (60)": [("services/performance.c", "dm_svc_perf_get_sp_stats"), ("services/thermal_pwr_mgmt.c", "Thermal_Pwr_Mgmt_Get_System_Power_Temp_Stats")],
    "DM_CMD_GET_MODULE_CURRENT_TEMPERATURE (27)": [("services/thermal_power_monitor.c", "pwr_svc_get_module_current_temperature"), ("services/thermal_pwr_mgmt.c", "get_module_current_temperature"),
                                                   ("driver/pvt_controller.c", "pvt_get_minion_avg_temperature"), ("driver/pvt_controller.c", "pvt_get_minion_avg_low_high_temperature"),
                                                   ("driver/pvt_controller.c", "pvt_get_ioshire_ts_sample"), ("driver/pvt_controller.c", "pvt_get_min_shire_ts_sample"), ("driver/pvt_controller.c", "pvt_get_ts_data")],
    "DM_CMD_GET_MODULE_VOLTAGE (31)": [("services/thermal_power_monitor.c", "pwr_svc_get_module_voltage"), ("services/thermal_pwr_mgmt.c", "get_module_voltage"),
                                       ("driver/pmic_controller.c", "pmic_get_voltage"), ("driver/pmic_controller.c", "get_pmic_reg"), ("driver/i2c_controller.c", "i2c_read")],
}
ROUTE = ("rtos_task/command_dispatcher.c", "pc_vq_process_pending_command")
MACROS = [("driver/pvt_controller.c", "GET_MINION_VM"), ("driver/pvt_controller.c", "GET_MEMSHIRE_VM")]
# what a store on the path touches: out-parameters and locals are not listed; the rest is sorted by what it reaches
CATS = [("a device register (the SP's I2C controller's command register: an I2C transaction)", re.compile(r"->regs->[A-Z_]+\s*=(?!=)")),
        ("a call that writes (error path or not: see the line)", re.compile(r"\b(i2c_soft_reset|set_pmic_reg|i2c_write|pmic_set_[a-z_]+|flash_fs_[a-z_]+|update_module_[a-z_]+|write_memshire_[a-z_]+|iowrite\w*)\s*\(")),
        ("SP RAM: a global (a copy of the value just read, or an error mark)", re.compile(r"\b(g_[a-z0-9_]+(\.[a-z0-9_\[\]]+)+|get_soc_perf_reg\(\)->[a-z0-9_.]+|pvt_bad_min_shire_mask)\s*(\|=|=)(?!=)"))]


def git(*a):
    return subprocess.run(["git", "-C", REPO] + list(a), check=True, capture_output=True, text=True).stdout


def body(rev, rel, name):
    src = git("show", f"{rev}:{B}/{rel}")
    lines = src.split("\n")
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
                    return "\n".join(out)
    return None


def macro(rev, rel, name):
    src = git("show", f"{rev}:{B}/{rel}").split("\n")
    for i, l in enumerate(src):
        if l.startswith(f"#define {name}("):
            out = []
            for l2 in src[i:]:
                out.append(l2)
                if not l2.rstrip().endswith("\\"):
                    return "\n".join(out)
    return None


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


print(f"E128 device-command audit. Public source: et-platform, BL2 0.18.0 line {FIRST} (first declaring 0.18.0) .. {LAST} (last before 0.19.0).")
a_, b_ = body(FIRST, *ROUTE), body(LAST, *ROUTE)
added = [l.strip() for l in b_.split("\n") if l not in a_.split("\n")]
print(f"Routing: {ROUTE[1]} in {ROUTE[0]}: identical across the line: {a_ == b_}; lines added on the line: {added}")
print()
for cmd, path in PATHS.items():
    print(f"== {cmd}")
    for rel, name in path:
        a, b = body(FIRST, rel, name), body(LAST, rel, name)
        st = stores(b or "")
        print(f"   {rel}:{name}: found {b is not None}; same at {FIRST} and {LAST}: {a == b}; stores other than locals: {len(st)}")
        for cat, line in st:
            print(f"      | [{cat}] {line}")
    print()
for rel, name in MACROS:
    a, b = macro(FIRST, rel, name), macro(LAST, rel, name)
    st = stores(b or "")
    print(f"== macro {name} ({rel}): found {b is not None}; same at both ends: {a == b}; stores other than locals: {len(st)}")
    for cat, line in st:
        print(f"      | [{cat}] {line}")
