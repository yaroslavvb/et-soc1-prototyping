# Device kernel, cross-compiled with the ET RISC-V toolchain of the open SDK.
# Adapted from https://github.com/marty1885/et-testdrive (Apache-2.0), as in the public lab repo's workloads.
cmake_minimum_required(VERSION 3.17)
project(x09mem-kernel LANGUAGES C CXX ASM)

include(DeviceUtils)  # add_riscv_executable(), from /opt/et/lib/cmake/cmake-modules

find_package(et-common-libs REQUIRED)

set(LINKER_SCRIPT ${CMAKE_CURRENT_SOURCE_DIR}/sections.ld)

add_riscv_executable(x09mem)
target_sources(x09mem.elf PRIVATE x09mem.c crt.S)
target_include_directories(x09mem.elf PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/..)
target_link_libraries(x09mem.elf PRIVATE et-common-libs::cm-umode)
set_target_properties(x09mem.elf PROPERTIES INTERPROCEDURAL_OPTIMIZATION TRUE)
