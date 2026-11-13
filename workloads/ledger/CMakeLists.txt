# The ledger's plain programs (copy, SHA-256, merge sort): device kernel + host program, one command to build both.
#   cmake -B build/ledger -S workloads/ledger -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && cmake --build build/ledger
#   ./build/ledger/host/ledger_host --sysemu --prog sha256 ...     # simulator (no device)
#   the card path needs --card explicitly (see host/main.cpp); this folder has never run on a card.
# Structure as workloads/enercat (adapted there from https://github.com/marty1885/et-testdrive, Apache-2.0).
# SPDX-License-Identifier: Apache-2.0
cmake_minimum_required(VERSION 3.17)
project(ledger VERSION 0.1.0)

include(ExternalProject)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_PREFIX_PATH}/lib/cmake")
list(APPEND CMAKE_MODULE_PATH "${CMAKE_PREFIX_PATH}/lib/cmake/cmake-modules")

set(KERNEL_BINARY_DIR ${CMAKE_BINARY_DIR}/kernel)
ExternalProject_Add(ledger_kernel
    SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/kernel
    BINARY_DIR ${KERNEL_BINARY_DIR}
    CMAKE_ARGS
        -DCMAKE_TOOLCHAIN_FILE=${CMAKE_PREFIX_PATH}/lib/cmake/riscv64-ec-toolchain.cmake
        -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}
        -DCMAKE_MODULE_PATH=${CMAKE_PREFIX_PATH}/lib/cmake/cmake-modules
        -DCMAKE_BUILD_TYPE=Release
        -DCMAKE_INSTALL_LIBDIR=lib
    INSTALL_COMMAND ""
    BUILD_ALWAYS TRUE
    BUILD_BYPRODUCTS ${KERNEL_BINARY_DIR}/ledger.elf
)

add_subdirectory(host)
add_dependencies(ledger_host ledger_kernel)
