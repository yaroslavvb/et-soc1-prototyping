# Device kernel, cross-compiled with the ET RISC-V toolchain (structure as in the lab repo's workloads/enercat).
cmake_minimum_required(VERSION 3.17)
project(x04clock-kernel LANGUAGES C CXX ASM)

include(DeviceUtils)  # add_riscv_executable(), from /opt/et/lib/cmake/cmake-modules

find_package(et-common-libs REQUIRED)

set(LINKER_SCRIPT ${CMAKE_CURRENT_SOURCE_DIR}/sections.ld)

add_riscv_executable(x04clock)
target_sources(x04clock.elf PRIVATE x04clock.c crt.S)
target_include_directories(x04clock.elf PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/.. ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(x04clock.elf PRIVATE et-common-libs::cm-umode)
