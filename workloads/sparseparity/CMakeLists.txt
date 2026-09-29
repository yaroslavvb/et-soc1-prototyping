# sparseparity workload: the noisy sparse-parity correlation scan (device kernel + host program + a CPU-only
# self-test), one command to build all three.
#   cmake -S workloads/sparseparity -B build/sparseparity-m1 -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev
#   nice cmake --build build/sparseparity-m1 -j4
#   build/sparseparity-m1/host/spp_selftest                    # CPU only: generator, closed forms, planner
#   build/sparseparity-m1/host/sparseparity_host --sysemu ...  # simulator
#   build/sparseparity-m1/host/sparseparity_host ...           # ET-SoC-1 card (/dev/et0_*): the owner's card time only
# Structure adapted from https://github.com/marty1885/et-testdrive (Apache-2.0).
cmake_minimum_required(VERSION 3.17)
project(sparseparity VERSION 0.1.0)

include(ExternalProject)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_PREFIX_PATH}/lib/cmake")
list(APPEND CMAKE_MODULE_PATH "${CMAKE_PREFIX_PATH}/lib/cmake/cmake-modules")

set(KERNEL_BINARY_DIR ${CMAKE_BINARY_DIR}/kernel)
ExternalProject_Add(sparseparity_kernel
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
    BUILD_BYPRODUCTS ${KERNEL_BINARY_DIR}/sparseparity.elf
)

add_subdirectory(host)
add_dependencies(sparseparity_host sparseparity_kernel)
