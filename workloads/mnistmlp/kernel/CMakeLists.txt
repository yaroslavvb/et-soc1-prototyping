# Device kernel, cross-compiled with the ET RISC-V toolchain (as workloads/ledger/kernel; adapted there from
# https://github.com/marty1885/et-testdrive, Apache-2.0).
# SPDX-License-Identifier: Apache-2.0
cmake_minimum_required(VERSION 3.17)
project(mnistmlp-kernel LANGUAGES C CXX ASM)

include(DeviceUtils)  # add_riscv_executable(), from /opt/et/lib/cmake/cmake-modules

find_package(et-common-libs REQUIRED)

set(LINKER_SCRIPT ${CMAKE_CURRENT_SOURCE_DIR}/sections.ld)

add_riscv_executable(mnistmlp)
target_sources(mnistmlp.elf PRIVATE mnistmlp.c crt.S)
target_include_directories(mnistmlp.elf PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/..)
target_link_libraries(mnistmlp.elf PRIVATE et-common-libs::cm-umode)
# No libc: keep GCC from turning small copy loops into memcpy or memset calls.
target_compile_options(mnistmlp.elf PRIVATE -fno-tree-loop-distribute-patterns)
set_target_properties(mnistmlp.elf PROPERTIES INTERPROCEDURAL_OPTIMIZATION TRUE)
