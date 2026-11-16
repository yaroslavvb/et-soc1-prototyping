# x09mem: memory traffic with designed data (device kernel + host program), one command to build both.
#   cmake -S . -B build -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && nice cmake --build build -j4
#   ./build/host/x09mem_host --list            # the arm table (no device)
#   ./build/host/x09mem_host --item wr.u4 ...  # a card (/dev/et<N>_ops)
# Structure adapted from https://github.com/marty1885/et-testdrive (Apache-2.0), as the public lab repo's workloads.
cmake_minimum_required(VERSION 3.17)
project(x09mem VERSION 0.1.0)

include(ExternalProject)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_PREFIX_PATH}/lib/cmake")
list(APPEND CMAKE_MODULE_PATH "${CMAKE_PREFIX_PATH}/lib/cmake/cmake-modules")

set(KERNEL_BINARY_DIR ${CMAKE_BINARY_DIR}/kernel)
ExternalProject_Add(x09mem_kernel
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
    BUILD_BYPRODUCTS ${KERNEL_BINARY_DIR}/x09mem.elf
)

add_subdirectory(host)
add_dependencies(x09mem_host x09mem_kernel)
