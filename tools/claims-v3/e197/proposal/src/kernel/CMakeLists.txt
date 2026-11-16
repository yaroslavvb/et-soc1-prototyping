# Device kernel, cross-compiled with the ET RISC-V toolchain.
# Adapted from https://github.com/marty1885/et-testdrive (Apache-2.0), as in the public lab repo's workloads.
cmake_minimum_required(VERSION 3.17)
project(regfile-kernel LANGUAGES C CXX ASM)

include(DeviceUtils)  # add_riscv_executable(), from /opt/et/lib/cmake/cmake-modules

find_package(et-common-libs REQUIRED)

set(LINKER_SCRIPT ${CMAKE_CURRENT_SOURCE_DIR}/sections.ld)

add_riscv_executable(regfile)
target_sources(regfile.elf PRIVATE regfile.c crt.S)
target_include_directories(regfile.elf PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/.. ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(regfile.elf PRIVATE et-common-libs::cm-umode)
set_target_properties(regfile.elf PROPERTIES INTERPROCEDURAL_OPTIMIZATION TRUE)
