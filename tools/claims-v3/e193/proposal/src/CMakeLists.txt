# x04clock: wait against spin, and which part of a core's clock a user program wakes.
#   cmake -S . -B build -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && cmake --build build -j4
#   ./build/host/x04clock_host --arm spin --t1 same --seconds 4              # card
# Structure as in the public lab repo's workloads/enercat (itself adapted from marty1885/et-testdrive, Apache-2.0).
cmake_minimum_required(VERSION 3.17)
project(x04clock VERSION 0.1.0)

include(ExternalProject)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_PREFIX_PATH}/lib/cmake")
list(APPEND CMAKE_MODULE_PATH "${CMAKE_PREFIX_PATH}/lib/cmake/cmake-modules")

set(KERNEL_BINARY_DIR ${CMAKE_BINARY_DIR}/kernel)
ExternalProject_Add(x04clock_kernel
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
    BUILD_BYPRODUCTS ${KERNEL_BINARY_DIR}/x04clock.elf
)

add_subdirectory(host)
add_dependencies(x04clock_host x04clock_kernel)
