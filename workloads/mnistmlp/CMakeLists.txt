# mnistmlp workload (E202): one forward pass of an int8 MLP over MNIST, device kernel + host program, one command to
# build both.
#   cmake -S workloads/mnistmlp -B build/mnistmlp -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev
#   nice cmake --build build/mnistmlp -j4
#   build/mnistmlp/host/mnistmlp_host --selftest                 # CPU only: packing, reference, splitmix64
#   build/mnistmlp/host/mnistmlp_host --ref ...                  # CPU only: the host's reference on a few groups
#   build/mnistmlp/host/mnistmlp_host --sysemu ...               # simulator
#   build/mnistmlp/host/mnistmlp_host --card ...                 # ET-SoC-1 card (/dev/et0_*): a registered card day only
# Structure as workloads/ledger (adapted there from https://github.com/marty1885/et-testdrive, Apache-2.0).
# SPDX-License-Identifier: Apache-2.0
cmake_minimum_required(VERSION 3.17)
project(mnistmlp VERSION 0.1.0)

include(ExternalProject)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_PREFIX_PATH}/lib/cmake")
list(APPEND CMAKE_MODULE_PATH "${CMAKE_PREFIX_PATH}/lib/cmake/cmake-modules")

set(KERNEL_BINARY_DIR ${CMAKE_BINARY_DIR}/kernel)
ExternalProject_Add(mnistmlp_kernel
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
    BUILD_BYPRODUCTS ${KERNEL_BINARY_DIR}/mnistmlp.elf
)

add_subdirectory(host)
add_dependencies(mnistmlp_host mnistmlp_kernel)
