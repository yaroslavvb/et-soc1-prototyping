# sparsity workload: sparse-compute probes (device kernel + host program), one command to build both.
#   cmake -B build -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && cmake --build build
#   ./build/host/sparsity_host --sysemu      # simulator
#   ./build/host/sparsity_host               # ET-SoC-1 card (/dev/et0_*)
# Structure adapted from https://github.com/marty1885/et-testdrive (Apache-2.0).
cmake_minimum_required(VERSION 3.17)
project(sparsity VERSION 0.1.0)

include(ExternalProject)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_PREFIX_PATH}/lib/cmake")
list(APPEND CMAKE_MODULE_PATH "${CMAKE_PREFIX_PATH}/lib/cmake/cmake-modules")

set(KERNEL_BINARY_DIR ${CMAKE_BINARY_DIR}/kernel)
ExternalProject_Add(sparsity_kernel
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
    BUILD_BYPRODUCTS ${KERNEL_BINARY_DIR}/sparsity.elf
)

add_subdirectory(host)
add_dependencies(sparsity_host sparsity_kernel)
