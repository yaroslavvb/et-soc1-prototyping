# Device kernel, cross-compiled with the ET RISC-V toolchain: an empty kernel, for timing the launch path.
# Adapted from https://github.com/marty1885/et-testdrive (Apache-2.0).
cmake_minimum_required(VERSION 3.17)
project(pciebench-kernel LANGUAGES C CXX ASM)

include(DeviceUtils)  # add_riscv_executable(), from /opt/et/lib/cmake/cmake-modules

find_package(et-common-libs REQUIRED)

set(LINKER_SCRIPT ${CMAKE_CURRENT_SOURCE_DIR}/sections.ld)

add_riscv_executable(empty)
target_sources(empty.elf PRIVATE empty.c crt.S)
target_link_libraries(empty.elf PRIVATE et-common-libs::cm-umode)
