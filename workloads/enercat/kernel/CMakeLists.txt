# Device kernel, cross-compiled with the ET RISC-V toolchain.
# Adapted from https://github.com/marty1885/et-testdrive (Apache-2.0).
cmake_minimum_required(VERSION 3.17)
project(enercat-kernel LANGUAGES C CXX ASM)

include(DeviceUtils)  # add_riscv_executable(), from /opt/et/lib/cmake/cmake-modules

find_package(et-common-libs REQUIRED)

set(LINKER_SCRIPT ${CMAKE_CURRENT_SOURCE_DIR}/sections.ld)

add_riscv_executable(enercat)
target_sources(enercat.elf PRIVATE enercat.c crt.S)
target_include_directories(enercat.elf PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/..)
target_link_libraries(enercat.elf PRIVATE et-common-libs::cm-umode)
set_target_properties(enercat.elf PROPERTIES INTERPROCEDURAL_OPTIMIZATION TRUE)
