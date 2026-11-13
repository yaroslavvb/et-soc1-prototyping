// E189's desk mock (Q167, the kit): stands in for the Constants.h CMake writes from either host's Constants.h.in. The desk build never
// starts a simulator and never opens a device: every path is "none". SPDX-License-Identifier: Apache-2.0
#pragma once
constexpr auto BOOTROM_TRAMPOLINE_TO_BL2_ELF = "none";
constexpr auto BL2_ELF = "none";
constexpr auto MASTER_MINION_ELF = "none";
constexpr auto MACHINE_MINION_ELF = "none";
constexpr auto WORKER_MINION_ELF = "none";
constexpr auto SYSEMU_INSTALL_DIR = "none";
constexpr auto KERNEL_ELF = "none";
