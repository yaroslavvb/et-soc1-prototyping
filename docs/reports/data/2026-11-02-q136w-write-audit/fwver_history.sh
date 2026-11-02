#!/usr/bin/env bash
# Q136(w): at each BL2 version bump of the public et-platform history (0.18.0 to 0.22.0), does the firmware-revisions
# query write the PMIC? It checks that firmware_update.c's handler calls pmic_get_fw_version, that pmic_get_fw_version
# calls the slot read and the subcommand, and that each of those calls set_pmic_reg on the firmware-management command
# register. Read-only git queries; run from the top of the lab repo, with the full et-platform clone at external/et-platform
# (or ET_PLATFORM=<path>). Output: fwver_history.txt beside this file.
set -u
G=${ET_PLATFORM:-external/et-platform}
F=device-bootloaders/CMakeLists.txt
P=device-bootloaders/src/ServiceProcessorBL2/driver/pmic_controller.c
U=device-bootloaders/src/ServiceProcessorBL2/services/firmware_update.c
git -C "$G" log --format='%h %ad' --date=short -G'project\(EsperantoBootLoader VERSION' -- "$F" | while read -r h d; do
  v=$(git -C "$G" show "$h:$F" 2>/dev/null | grep -o -E 'EsperantoBootLoader VERSION [0-9.]+' | awk '{print $3}')
  case "$v" in 0.18.*|0.19.*|0.20.*|0.21.*|0.22.*) ;; *) continue ;; esac
  body=$(git -C "$G" show "$h:$P" 2>/dev/null | awk '/^int pmic_get_fw_version\(/,/^}/')
  slot=$(git -C "$G" show "$h:$P" 2>/dev/null | awk '/^static int pmic_get_active_boot_slot\(/,/^}/' | grep -c 'set_pmic_reg(PMIC_I2C_FW_MGMTCMD_ADDRESS')
  sub=$(git -C "$G" show "$h:$P" 2>/dev/null | awk '/^static int pmic_fw_update_subcommand\(/,/^}/' | grep -c 'set_pmic_reg(PMIC_I2C_FW_MGMTCMD_ADDRESS')
  calls=$(printf '%s\n' "$body" | grep -c -E 'pmic_get_active_boot_slot|pmic_fw_update_subcommand')
  handler=$(git -C "$G" show "$h:$U" 2>/dev/null | grep -c 'pmic_get_fw_version(')
  echo "$h $d BL2 $v: firmware_update.c calls pmic_get_fw_version: $handler; it calls slot/subcommand: $calls; set_pmic_reg(FW_MGMTCMD) in slot $slot, in subcommand $sub"
done
